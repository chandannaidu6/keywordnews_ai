import torch
import asyncio
import re
import json
import logging
from typing import Dict, List, Optional
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from langchain.prompts import PromptTemplate
from langchain_community.llms import HuggingFacePipeline

from models import Article  # Make sure you have your Article model in models.py

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContentAnalysisState(BaseModel):
    content: dict
    analysis_result: Optional[dict] = None
    summary: Optional[str] = None
    relevance_score: Optional[float] = None
    metadata: Dict = {}

class NewsAnalysisAgent:
    def __init__(self):
        self.model_path = "gpt2"  # CPU-friendly GPT-2 for demonstration
        self.setup_model()
        self.setup_chains()

    def setup_model(self):
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            # GPT-2 doesn't have a true pad token
            self.tokenizer.pad_token = self.tokenizer.eos_token

            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                torch_dtype=torch.float32
            )
            self.model.to("cpu")

            self.text_generator = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                max_length=512,
                pad_token_id=self.tokenizer.eos_token_id,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                num_return_sequences=1,
            )
            self.llm = HuggingFacePipeline(pipeline=self.text_generator)

        except Exception as e:
            logger.error(f"Error in model setup: {e}")
            raise

    def setup_chains(self):
        """
        IMPORTANT: Escape braces inside the JSON example using double braces
        to avoid them being treated as variables by PromptTemplate.
        """

        # We double the braces in the example JSON: {{ ... }}
        relevance_template = """Analyze this content and return a JSON object with relevance metrics:

Content: {content}

Return ONLY valid JSON, no extra text. For example:
{{
    "relevance_score": 0.75,
    "reasoning": "Brief explanation",
    "credibility": "high/medium/low"
}}
"""

        self.relevance_chain = (
            PromptTemplate(
                input_variables=["content"],
                template=relevance_template
            )
            | self.llm
        )

        # Summarization
        summary_template = """Summarize this content in 2-3 sentences:

Content: {content}

Summary:
"""
        self.summary_chain = (
            PromptTemplate(
                input_variables=["content"],
                template=summary_template
            )
            | self.llm
        )

    def extract_json(self, text: str) -> dict:
        """Safely extract the JSON snippet from the model's text output."""
        try:
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if not match:
                return {}
            json_str = match.group(0)
            return json.loads(json_str)
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse JSON from: {text[:100]}...")
            return {}

    async def analyze_relevance(self, state: ContentAnalysisState) -> ContentAnalysisState:
        """Generate a short JSON about relevance, parse, and store it."""
        try:
            text_input = state.content.get("content", "")[:1000]  # limit length
            raw_result = await asyncio.get_event_loop().run_in_executor(
                None,
                self.relevance_chain.invoke,
                {"content": text_input}
            )

            analysis_dict = self.extract_json(raw_result)
            state.analysis_result = analysis_dict
            state.relevance_score = float(analysis_dict.get("relevance_score", 0.0))

        except Exception as e:
            logger.error(f"Relevance analysis error: {e}")
            state.analysis_result = {}
            state.relevance_score = 0.0
        return state

    async def generate_summary(self, state: ContentAnalysisState) -> ContentAnalysisState:
        """If content is relevant enough, generate a short summary."""
        if state.relevance_score >= 0.6:
            try:
                text_input = state.content.get("content", "")[:1000]
                raw_summary = await asyncio.get_event_loop().run_in_executor(
                    None,
                    self.summary_chain.invoke,
                    {"content": text_input}
                )
                state.summary = raw_summary.strip()
            except Exception as e:
                logger.error(f"Summary generation error: {e}")
                state.summary = None
        return state

    def should_create_article(self, state: ContentAnalysisState) -> bool:
        """Decide if we produce an Article object from state."""
        return (
            state.relevance_score and state.relevance_score >= 0.6 and
            state.summary and len(state.summary.strip()) > 20
        )

    async def create_article(self, state: ContentAnalysisState) -> Article:
        """Construct the final Article Pydantic object."""
        return Article(
            title=state.content.get("title", ""),
            summary=state.summary or "",
            url=state.content.get("url", ""),
            source=state.content.get("source", "")
        )

    async def process_content(self, contents: List[Dict]) -> List[Article]:
        """Overall pipeline for multiple contents."""
        articles = []
        for content_item in contents:
            try:
                state = ContentAnalysisState(content=content_item)
                # 1) Relevance
                state = await self.analyze_relevance(state)
                # 2) Summary
                state = await self.generate_summary(state)
                # 3) Possibly create an article
                if self.should_create_article(state):
                    article = await self.create_article(state)
                    articles.append(article)
            except Exception as e:
                logger.error(f"Content error: {e}")
        return articles

async def filter_and_summarize(contents: List[Dict]) -> List[Article]:
    """Main entry point to run the pipeline."""
    try:
        agent = NewsAnalysisAgent()
        return await agent.process_content(contents)
    except Exception as e:
        logger.error(f"Filter and summarize error: {e}")
        return []

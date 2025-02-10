import torch
import asyncio
import re
import json
import difflib
import logging
from typing import Dict, List, Optional
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from langchain.prompts import PromptTemplate
from langchain_community.llms import HuggingFacePipeline
from app.models import Article

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContentAnalysisState(BaseModel):
    content: dict
    analysis_result: Optional[dict] = None
    summary: Optional[str] = None
    relevance_score: Optional[float] = None
    metadata: Dict = {}

def is_similar(line1: str, line2: str, threshold: float = 0.9) -> bool:
    """Increased threshold to be more lenient with similarity"""
    return difflib.SequenceMatcher(None, line1, line2).ratio() > threshold

class NewsAnalysisAgent:
    def __init__(self):
        self.model_path = "gpt2"  
        self.setup_model()
        self.setup_chains()

    def setup_model(self):
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
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
                max_new_tokens=150,    
                pad_token_id=self.tokenizer.eos_token_id,
                do_sample=True,
                temperature=0.8,      
                top_k=50,
                top_p=0.95,          
                num_beams=3,        
                repetition_penalty=1.5,  
                length_penalty=1.2,   
                no_repeat_ngram_size=2,  
                num_return_sequences=1,
            )
            self.llm = HuggingFacePipeline(pipeline=self.text_generator)
        except Exception as e:
            logger.error(f"Error in model setup: {str(e)}")
            raise

    def setup_chains(self):
        # Simplified relevance template
        relevance_template = """Rate the relevance of this content from 0.0 to 1.0 and return as JSON:
Content: {content}
{{ "relevance_score": <score>, "reasoning": "<reason>" }}"""

        self.relevance_chain = (
            PromptTemplate(input_variables=["content"], template=relevance_template)
            | self.llm
        )

        # Simplified summary template
        summary_template = """Write a short summary of this article in a few sentences:
{content}
Summary:"""
        
        self.summary_chain = (
            PromptTemplate(input_variables=["content"], template=summary_template)
            | self.llm
        )

    def extract_json(self, text: str) -> dict:
        try:
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            
            number_match = re.search(r"0\.\d+|1\.0|1", text)
            if number_match:
                return {"relevance_score": float(number_match.group(0))}
            
            return {"relevance_score": 0.5}  
        except Exception as e:
            logger.warning(f"JSON extraction failed: {str(e)}")
            return {"relevance_score": 0.5}  

    def remove_repeated_or_prompt_lines(self, text: str) -> str:
        """
        Removes prompt text, duplicates, and unwanted phrases from generated summaries.
        Returns cleaned text.
        """
        text = text.replace("Write a short summary of this article in a few sentences:\n", "")
        
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        
        filtered = []
        skip_phrases = ["summary:", "content:", "article:", "guidelines:"]
        
        for line in lines:
            lower_line = line.lower()
            if any(phrase in lower_line for phrase in skip_phrases):
                continue
            
            is_duplicate = False
            for existing in filtered:
                if is_similar(lower_line, existing.lower()):
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                filtered.append(line)
        
        return "\n".join(filtered[:7])   # Limit to 7 lines

    async def analyze_relevance(self, state: ContentAnalysisState) -> ContentAnalysisState:
        try:
            text_input = state.content.get("content", "")
            if not text_input:
                state.relevance_score = 0.0
                return state
                
            if any(term in text_input.lower() for term in ["kohli", "virat", "india", "cricket"]):
                state.relevance_score = 0.9
                return state
            
            raw_result = await asyncio.get_event_loop().run_in_executor(
                None, self.relevance_chain.invoke, {"content": text_input[:500]}
            )
            analysis_dict = self.extract_json(raw_result)
            state.relevance_score = float(analysis_dict.get("relevance_score", 0.5))
        except Exception as e:
            logger.error(f"Relevance analysis error: {str(e)}")
            state.relevance_score = 0.5  # Default to middle score instead of 0
        return state

    async def generate_summary(self, state: ContentAnalysisState) -> ContentAnalysisState:
        if (state.relevance_score or 0.0) >= 0.4:  # Lowered threshold
            try:
                text_input = state.content.get("content", "")
                if not text_input:
                    return state
                    
                raw_summary = await asyncio.get_event_loop().run_in_executor(
                    None, self.summary_chain.invoke, {"content": text_input[:500]}
                )
                
                if len(text_input) < 100:
                    state.summary = text_input
                else:
                    cleaned_summary = self.remove_repeated_or_prompt_lines(raw_summary)
                    if cleaned_summary:
                        state.summary = cleaned_summary
            except Exception as e:
                logger.error(f"Summary generation error: {str(e)}")
        return state

    def should_create_article(self, state: ContentAnalysisState) -> bool:
        """Relaxed criteria for article creation"""
        if not state.summary:
            return False
            
        return (
            state.relevance_score >= 0.4  
            and len(state.summary.strip()) > 10 
        )

    async def create_article(self, state: ContentAnalysisState) -> Article:
        summary = state.summary if state.summary else state.content.get("content", "")
        return Article(
            title=state.content.get("title", ""),
            summary=summary,
            url=state.content.get("url", ""),
            source=state.content.get("source", "")
        )

    async def process_content(self, contents: List[Dict]) -> List[Article]:
        articles = []
        for content_item in contents:
            try:
                if not content_item.get("content"):
                    continue
                    
                state = ContentAnalysisState(content=content_item)
                state = await self.analyze_relevance(state)
                state = await self.generate_summary(state)
                
                if self.should_create_article(state):
                    article = await self.create_article(state)
                    articles.append(article)
                    
            except Exception as e:
                logger.error(f"Content processing error: {str(e)}")
                
        return articles

async def filter_and_summarize(contents: List[Dict]) -> List[Article]:
    try:
        agent = NewsAnalysisAgent()
        articles = await agent.process_content(contents)
        logger.info(f"Processed {len(contents)} items into {len(articles)} articles")
        return articles
    except Exception as e:
        logger.error(f"Filter and summarize error: {str(e)}")
        return []
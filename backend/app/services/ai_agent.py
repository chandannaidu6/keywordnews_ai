from typing import Dict, List, Tuple, Optional
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain.llms import HuggingFacePipeline
from langchain.schema import AgentAction, AgentFinish
from langgraph.graph import StateGraph, END  # Fixed import
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from app.models import Article
from app.utils.config import get_model_path
import torch
import asyncio
from pydantic import BaseModel

class ContentAnalysisState(BaseModel):
    content: dict
    analysis_result: Optional[dict] = None
    summary: Optional[str] = None
    relevance_score: Optional[float] = None
    metadata: Dict = {}

class NewsAnalysisAgent:  # Fixed class name typo
    def __init__(self):
        self.model_path = get_model_path()
        self.setup_model()
        self.setup_chains()
        self.setup_graph()  # Fixed method name

    def setup_model(self):
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_path,
            device_map="auto",
            torch_dtype=torch.float16,
            load_in_4bit=True
        )
        self.text_generator = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            device=0 if torch.cuda.is_available() else -1,  # Fixed syntax
            max_length=512,
            num_beams=5,
            no_repeat_ngram_size=2,
            early_stopping=True
        )

        self.llm = HuggingFacePipeline(pipeline=self.text_generator)

    def setup_chains(self):
        """Setup various LLM chains for different tasks"""
        relevance_template = """Analyze the following content for relevance and accuracy:
        {content}
        
        Criteria:
        1. Information accuracy
        2. Source credibility
        3. Timeliness
        4. Public interest
        
        Output a JSON with:
        - relevance_score (0-1)
        - reasoning
        - credibility_assessment"""

        self.relevance_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                input_variables=["content"],
                template=relevance_template
            )
        )

        summary_template = """Provide a concise, informative summary of the following content:
        {content}
        
        Requirements:
        1. Maximum 3 sentences
        2. Include key facts and figures
        3. Maintain objective tone
        4. Highlight main implications
        
        Summary:"""

        self.summary_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                input_variables=["content"],
                template=summary_template
            )
        )

    def setup_graph(self):  # Fixed method name
        """Setup the workflow graph"""
        self.workflow = StateGraph(ContentAnalysisState)

        # Add nodes
        self.workflow.add_node("analyze_relevance", self.analyze_relevance)
        self.workflow.add_node("generate_summary", self.generate_summary)
        self.workflow.add_node("create_article", self.create_article)

        # Add edges
        self.workflow.add_edge("analyze_relevance", "generate_summary")  # Fixed method name
        self.workflow.add_conditional_edges(  # Fixed method name
            "generate_summary",
            self.should_create_article,
            {
                True: "create_article",
                False: END
            }
        )
        self.workflow.add_edge("create_article", END)

        self.workflow.set_entry_point("analyze_relevance")

    async def analyze_relevance(self, state: ContentAnalysisState) -> ContentAnalysisState:
        """Analyze content relevance"""
        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                self.relevance_chain.run,
                state.content['content']
            )
            state.analysis_result = eval(result)
            state.relevance_score = state.analysis_result['relevance_score']
            return state  # Added missing return
        except Exception as e:
            print(f'Error in relevance analysis: {e}')
            state.relevance_score = 0
            return state

    async def generate_summary(self, state: ContentAnalysisState) -> ContentAnalysisState:
        """Generate summary for relevant content"""
        if state.relevance_score >= 0.7:  # Fixed comparison operator
            try:
                summary = await asyncio.get_event_loop().run_in_executor(
                    None,
                    self.summary_chain.run,
                    state.content['content']
                )
                state.summary = summary.strip()
            except Exception as e:
                print(f"Error in summary generation: {e}")
        return state

    def should_create_article(self, state: ContentAnalysisState) -> bool:
        """Determine if article should be created"""
        return (
            state.relevance_score >= 0.7 and
            state.summary is not None and
            len(state.summary.strip()) > 0
        )

    async def create_article(self, state: ContentAnalysisState) -> ContentAnalysisState:
        """Create article from analyzed content"""
        try:
            article = Article(
                title=state.content.get('title', ''),  # Fixed syntax
                summary=state.summary,
                url=state.content.get('url', ''),
                source=state.content.get('source', '')
            )
            state.metadata['article'] = article
        except Exception as e:
            print(f"Error creating article: {e}")
        return state

    async def process_content(self, contents: List[Dict]) -> List[Article]:
        """Process multiple content items"""
        articles = []
        for content in contents:
            try:
                state = ContentAnalysisState(content=content)
                final_state = await self.workflow.arun(state)

                if 'article' in final_state.metadata:
                    articles.append(final_state.metadata['article'])
            except Exception as e:
                print(f"Error processing content: {e}")
                continue
        return articles

# Main function
async def filter_and_summarize(contents: List[Dict]) -> List[Article]:
    """Main function to filter and summarize content"""
    agent = NewsAnalysisAgent()
    return await agent.process_content(contents)
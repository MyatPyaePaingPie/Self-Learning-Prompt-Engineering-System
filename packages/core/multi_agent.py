"""
Multi-Agent System for Prompt Optimization
Base classes and specialized agents
"""

import os
import json
import logging
from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from groq import Groq

from packages.core.model_config import ModelConfig, get_model_for_agent
from packages.core.agent_registry import register_agent
from packages.core.token_tracker import TokenTracker, TokenUsage

logger = logging.getLogger(__name__)
tracker = TokenTracker()


# Response Models
class AgentAnalysis(BaseModel):
    """Agent's analysis of a prompt"""
    score: float  # 0-10
    strengths: List[str]
    weaknesses: List[str]


class AgentSuggestions(BaseModel):
    """Agent's proposed improvements"""
    suggestions: List[str]
    improved_prompt: str
    confidence: float  # 0-1


class AgentResult(BaseModel):
    """Complete agent result with token tracking"""
    agent_name: str
    analysis: AgentAnalysis
    suggestions: AgentSuggestions
    metadata: Dict[str, Any]
    token_usage: Optional[Dict[str, Any]] = None  # Token usage for this agent's execution


# Base Agent Interface
class AgentInterface(ABC):
    """
    Base interface for all agents.
    Each agent specializes in one aspect of prompt optimization.
    """
    
    name: str = None  # Set by subclass
    
    def __init__(self, model_config: Optional[ModelConfig] = None):
        """
        Initialize agent with model configuration.
        If model_config not provided, uses default from registry.
        
        Args:
            model_config: Model configuration (optional, defaults to registry mapping)
        """
        self.model_config = model_config or get_model_for_agent(self.name)
        self._initialize_prompts()
    
    @abstractmethod
    def _initialize_prompts(self):
        """
        Initialize agent-specific prompts (called after model_config set).
        Subclasses must set self.analysis_prompt and self.improvement_prompt.
        """
        pass
    
    async def _call_llm(self, system_prompt: str, user_prompt: str, max_retries: int = 3) -> tuple[str, Optional[TokenUsage]]:
        """
        Call LLM with agent's configured model and track token usage.
        Follows engine.py improve_prompt() pattern with retry logic.
        
        Args:
            system_prompt: System prompt
            user_prompt: User prompt
            max_retries: Maximum retry attempts
        
        Returns:
            Tuple of (LLM response text, TokenUsage object)
        """
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        for attempt in range(max_retries):
            try:
                response = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    model=self.model_config.model_id,
                    temperature=self.model_config.temperature,
                    max_tokens=self.model_config.max_tokens,
                )
                
                result = response.choices[0].message.content.strip()
                
                # Track token usage (capture return value)
                usage = tracker.track_llm_call(
                    system_prompt + "\n\n" + user_prompt,
                    result,
                    self.model_config.model_id
                )
                
                return result, usage
                
            except Exception as e:
                error_msg = str(e)
                wait_time = 2 ** attempt if attempt < max_retries - 1 else 0
                
                if attempt == max_retries - 1:
                    logger.error(
                        f"{self.name} agent: All {max_retries} attempts failed.",
                        exc_info=True
                    )
                    return f"[Error: {error_msg}]", None
                
                if wait_time > 0:
                    logger.info(f"{self.name} agent: Retrying in {wait_time} seconds...")
                    import time
                    time.sleep(wait_time)
        
        return "[Error: Unable to generate response]", None
    
    @abstractmethod
    async def analyze(self, prompt: str) -> AgentAnalysis:
        """
        Analyze prompt and return assessment.
        
        Args:
            prompt: Prompt text to analyze
        
        Returns:
            AgentAnalysis with score, strengths, weaknesses
        """
        pass
    
    @abstractmethod
    async def propose_improvements(self, prompt: str, analysis: AgentAnalysis) -> AgentSuggestions:
        """
        Propose concrete improvements based on analysis.
        
        Args:
            prompt: Original prompt text
            analysis: Previous analysis result
        
        Returns:
            AgentSuggestions with suggestions, improved prompt, confidence
        """
        pass
    
    async def run(self, prompt: str) -> AgentResult:
        """
        Full agent execution (analyze + propose) with token tracking.
        
        Args:
            prompt: Prompt text to optimize
        
        Returns:
            Complete AgentResult with token usage
        """
        # Execute agent pipeline
        analysis = await self.analyze(prompt)
        suggestions = await self.propose_improvements(prompt, analysis)
        
        # Aggregate token usage from both calls
        total_usage = None
        if hasattr(self, '_last_token_usage') and self._last_token_usage:
            total_usage = {
                "prompt_tokens": self._last_token_usage.get("prompt_tokens", 0),
                "completion_tokens": self._last_token_usage.get("completion_tokens", 0),
                "total_tokens": self._last_token_usage.get("total_tokens", 0),
                "cost_usd": self._last_token_usage.get("cost_usd", 0.0),
                "model": self.model_config.model_id
            }
        
        return AgentResult(
            agent_name=self.name,
            analysis=analysis,
            suggestions=suggestions,
            metadata=self.get_metadata(),
            token_usage=total_usage
        )
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Return agent-specific metadata.
        
        Returns:
            Dictionary with agent metadata
        """
        return {
            "focus": self.name,
            "model_id": self.model_config.model_id,
            "model_name": self.model_config.display_name
        }


# Specialized Agents

@register_agent(
    display_name="Syntax Agent",
    description="Analyzes clarity, role definition, and explicit instructions",
    focus_areas=["role", "clarity", "precision", "terminology"]
)
class SyntaxAgent(AgentInterface):
    """Agent focused on syntax and clarity"""
    
    name = "syntax"
    
    def _initialize_prompts(self):
        """Initialize syntax-specific prompts"""
        self.analysis_prompt = """You are a syntax and clarity expert for prompt engineering.
Focus ONLY on:
- Clear role definition ("You are a...")
- Explicit instructions and expectations
- Removal of ambiguity
- Precise language and terminology

Score the prompt on these criteria (0-10 scale).
Return ONLY a JSON object:
{
  "score": <float 0-10>,
  "strengths": [<str>],
  "weaknesses": [<str>]
}"""
        
        self.improvement_prompt = """You are a syntax and clarity expert for prompt engineering.
Improve this prompt by focusing ONLY on:
- Adding clear role definition
- Making instructions explicit
- Removing ambiguity
- Using precise language

Return ONLY a JSON object:
{
  "suggestions": [<str>],
  "improved_prompt": <str>,
  "confidence": <float 0-1>
}"""
    
    async def analyze(self, prompt: str) -> AgentAnalysis:
        """Analyze prompt syntax and clarity"""
        response, usage = await self._call_llm(
            self.analysis_prompt,
            f"Analyze this prompt:\n\n{prompt}"
        )
        
        # Initialize token tracking
        if not hasattr(self, '_last_token_usage'):
            self._last_token_usage = {}
        
        # Aggregate token usage (analysis call)
        if usage:
            self._last_token_usage = {
                "prompt_tokens": usage.prompt_tokens,
                "completion_tokens": usage.completion_tokens,
                "total_tokens": usage.total_tokens,
                "cost_usd": usage.cost_usd
            }
        
        # Parse JSON response
        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            data = json.loads(response)
            return AgentAnalysis(
                score=float(data["score"]),
                strengths=data.get("strengths", []),
                weaknesses=data.get("weaknesses", [])
            )
        except Exception as e:
            logger.error(f"Syntax agent analysis parsing error: {e}")
            return AgentAnalysis(
                score=5.0,
                strengths=["Unable to parse response"],
                weaknesses=["Analysis failed"]
            )
    
    async def propose_improvements(self, prompt: str, analysis: AgentAnalysis) -> AgentSuggestions:
        """Propose syntax improvements"""
        response, usage = await self._call_llm(
            self.improvement_prompt,
            f"Improve this prompt:\n\n{prompt}\n\nWeaknesses found: {', '.join(analysis.weaknesses)}"
        )
        
        # Aggregate token usage (improvement call)
        if usage and hasattr(self, '_last_token_usage'):
            self._last_token_usage["prompt_tokens"] += usage.prompt_tokens
            self._last_token_usage["completion_tokens"] += usage.completion_tokens
            self._last_token_usage["total_tokens"] += usage.total_tokens
            self._last_token_usage["cost_usd"] += usage.cost_usd
        
        # Parse JSON response
        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            data = json.loads(response)
            return AgentSuggestions(
                suggestions=data.get("suggestions", []),
                improved_prompt=data.get("improved_prompt", prompt),
                confidence=float(data.get("confidence", 0.5))
            )
        except Exception as e:
            logger.error(f"Syntax agent improvement parsing error: {e}")
            return AgentSuggestions(
                suggestions=["Unable to generate improvements"],
                improved_prompt=prompt,
                confidence=0.5
            )


@register_agent(
    display_name="Structure Agent",
    description="Analyzes organization, formatting, and logical flow",
    focus_areas=["organization", "formatting", "flow", "sections"]
)
class StructureAgent(AgentInterface):
    """Agent focused on structure and formatting"""
    
    name = "structure"
    
    def _initialize_prompts(self):
        """Initialize structure-specific prompts"""
        self.analysis_prompt = """You are a structure and formatting expert for prompt engineering.
Focus ONLY on:
- Logical organization (sections, bullets, headings)
- Step-by-step flow
- Clear deliverables and constraints sections
- Proper formatting (bullets, numbering, whitespace)

Score the prompt on these criteria (0-10 scale).
Return ONLY a JSON object:
{
  "score": <float 0-10>,
  "strengths": [<str>],
  "weaknesses": [<str>]
}"""
        
        self.improvement_prompt = """You are a structure and formatting expert for prompt engineering.
Improve this prompt by focusing ONLY on:
- Adding logical organization
- Creating clear sections
- Adding step-by-step flow
- Improving formatting

Return ONLY a JSON object:
{
  "suggestions": [<str>],
  "improved_prompt": <str>,
  "confidence": <float 0-1>
}"""
    
    async def analyze(self, prompt: str) -> AgentAnalysis:
        """Analyze prompt structure"""
        response, usage = await self._call_llm(
            self.analysis_prompt,
            f"Analyze this prompt:\n\n{prompt}"
        )
        
        # Initialize token tracking
        if not hasattr(self, '_last_token_usage'):
            self._last_token_usage = {}
        
        # Aggregate token usage (analysis call)
        if usage:
            self._last_token_usage = {
                "prompt_tokens": usage.prompt_tokens,
                "completion_tokens": usage.completion_tokens,
                "total_tokens": usage.total_tokens,
                "cost_usd": usage.cost_usd
            }
        
        # Parse JSON response (same pattern as SyntaxAgent)
        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            data = json.loads(response)
            return AgentAnalysis(
                score=float(data["score"]),
                strengths=data.get("strengths", []),
                weaknesses=data.get("weaknesses", [])
            )
        except Exception as e:
            logger.error(f"Structure agent analysis parsing error: {e}")
            return AgentAnalysis(
                score=5.0,
                strengths=["Unable to parse response"],
                weaknesses=["Analysis failed"]
            )
    
    async def propose_improvements(self, prompt: str, analysis: AgentAnalysis) -> AgentSuggestions:
        """Propose structure improvements"""
        response, usage = await self._call_llm(
            self.improvement_prompt,
            f"Improve this prompt:\n\n{prompt}\n\nWeaknesses found: {', '.join(analysis.weaknesses)}"
        )
        
        # Aggregate token usage (improvement call)
        if usage and hasattr(self, '_last_token_usage'):
            self._last_token_usage["prompt_tokens"] += usage.prompt_tokens
            self._last_token_usage["completion_tokens"] += usage.completion_tokens
            self._last_token_usage["total_tokens"] += usage.total_tokens
            self._last_token_usage["cost_usd"] += usage.cost_usd
        
        # Parse JSON response
        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            data = json.loads(response)
            return AgentSuggestions(
                suggestions=data.get("suggestions", []),
                improved_prompt=data.get("improved_prompt", prompt),
                confidence=float(data.get("confidence", 0.5))
            )
        except Exception as e:
            logger.error(f"Structure agent improvement parsing error: {e}")
            return AgentSuggestions(
                suggestions=["Unable to generate improvements"],
                improved_prompt=prompt,
                confidence=0.5
            )


@register_agent(
    display_name="Domain Agent",
    description="Analyzes domain context, terminology, and examples",
    focus_areas=["domain", "context", "examples", "terminology"]
)
class DomainAgent(AgentInterface):
    """Agent focused on domain expertise"""
    
    name = "domain"
    
    def _initialize_prompts(self):
        """Initialize domain-specific prompts"""
        self.analysis_prompt = """You are a domain context expert for prompt engineering.
Focus ONLY on:
- Domain detection (coding, marketing, creative, technical)
- Context enrichment (add domain-specific terminology)
- Examples and edge cases relevant to domain
- Domain-specific constraints and best practices

Score the prompt on these criteria (0-10 scale).
Return ONLY a JSON object:
{
  "score": <float 0-10>,
  "strengths": [<str>],
  "weaknesses": [<str>]
}"""
        
        self.improvement_prompt = """You are a domain context expert for prompt engineering.
Improve this prompt by focusing ONLY on:
- Adding domain-specific context
- Including relevant terminology
- Adding examples and edge cases
- Including domain best practices

Return ONLY a JSON object:
{
  "suggestions": [<str>],
  "improved_prompt": <str>,
  "confidence": <float 0-1>
}"""
    
    async def analyze(self, prompt: str) -> AgentAnalysis:
        """Analyze prompt domain context"""
        response, usage = await self._call_llm(
            self.analysis_prompt,
            f"Analyze this prompt:\n\n{prompt}"
        )
        
        # Initialize token tracking
        if not hasattr(self, '_last_token_usage'):
            self._last_token_usage = {}
        
        # Aggregate token usage (analysis call)
        if usage:
            self._last_token_usage = {
                "prompt_tokens": usage.prompt_tokens,
                "completion_tokens": usage.completion_tokens,
                "total_tokens": usage.total_tokens,
                "cost_usd": usage.cost_usd
            }
        
        # Parse JSON response (same pattern as other agents)
        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            data = json.loads(response)
            return AgentAnalysis(
                score=float(data["score"]),
                strengths=data.get("strengths", []),
                weaknesses=data.get("weaknesses", [])
            )
        except Exception as e:
            logger.error(f"Domain agent analysis parsing error: {e}")
            return AgentAnalysis(
                score=5.0,
                strengths=["Unable to parse response"],
                weaknesses=["Analysis failed"]
            )
    
    async def propose_improvements(self, prompt: str, analysis: AgentAnalysis) -> AgentSuggestions:
        """Propose domain improvements"""
        response, usage = await self._call_llm(
            self.improvement_prompt,
            f"Improve this prompt:\n\n{prompt}\n\nWeaknesses found: {', '.join(analysis.weaknesses)}"
        )
        
        # Aggregate token usage (improvement call)
        if usage and hasattr(self, '_last_token_usage'):
            self._last_token_usage["prompt_tokens"] += usage.prompt_tokens
            self._last_token_usage["completion_tokens"] += usage.completion_tokens
            self._last_token_usage["total_tokens"] += usage.total_tokens
            self._last_token_usage["cost_usd"] += usage.cost_usd
        
        # Parse JSON response
        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            data = json.loads(response)
            return AgentSuggestions(
                suggestions=data.get("suggestions", []),
                improved_prompt=data.get("improved_prompt", prompt),
                confidence=float(data.get("confidence", 0.5))
            )
        except Exception as e:
            logger.error(f"Domain agent improvement parsing error: {e}")
            return AgentSuggestions(
                suggestions=["Unable to generate improvements"],
                improved_prompt=prompt,
                confidence=0.5
            )


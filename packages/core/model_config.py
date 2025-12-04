"""
Model Configuration for Multi-Agent System
Centralized registry for Groq models (L:VI - Centralized Innovation)
"""

from dataclasses import dataclass
from typing import Dict
from enum import Enum


class ModelSpeed(Enum):
    """Model speed classification"""
    FASTEST = "fastest"
    FAST = "fast"
    MODERATE = "moderate"
    SLOW = "slow"


class ModelCost(Enum):
    """Model cost classification"""
    LOWEST = "lowest"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


@dataclass
class ModelConfig:
    """Configuration for a Groq model"""
    model_id: str
    display_name: str
    speed: ModelSpeed
    cost: ModelCost
    use_case: str
    max_tokens: int = 2048
    temperature: float = 0.7


# Model Registry (SSOT - Single Source of Truth)
MODEL_REGISTRY: Dict[str, ModelConfig] = {
    "fast": ModelConfig(
        model_id="llama-3.1-8b-instant",
        display_name="Llama 3.1 8B (Fast)",
        speed=ModelSpeed.FASTEST,
        cost=ModelCost.LOWEST,
        use_case="Quick syntax and structure analysis",
        max_tokens=1024,
        temperature=0.5  # More deterministic for syntax
    ),
    
    "balanced": ModelConfig(
        model_id="llama-3.3-70b-versatile",
        display_name="Llama 3.3 70B (Balanced)",
        speed=ModelSpeed.MODERATE,
        cost=ModelCost.MODERATE,
        use_case="General purpose, current default",
        max_tokens=2048,
        temperature=0.7
    ),
    
    "powerful": ModelConfig(
        model_id="llama-3.3-70b-versatile",
        display_name="Llama 3.3 70B (Powerful)",
        speed=ModelSpeed.MODERATE,
        cost=ModelCost.MODERATE,  # Same price as balanced (3.1-70b is decommissioned)
        use_case="Deep domain analysis and reasoning",
        max_tokens=2048,
        temperature=0.8  # More creative for domain
    ),
    
    "alternative": ModelConfig(
        model_id="gemma2-9b-it",
        display_name="Gemma 2 9B",
        speed=ModelSpeed.FAST,
        cost=ModelCost.LOW,
        use_case="Alternative perspective for diversity",
        max_tokens=1024,
        temperature=0.7
    ),
    
    "expert": ModelConfig(
        model_id="mixtral-8x7b-32768",
        display_name="Mixtral 8x7B",
        speed=ModelSpeed.MODERATE,
        cost=ModelCost.MODERATE,
        use_case="Complex multi-faceted analysis",
        max_tokens=2048,
        temperature=0.7
    )
}


# Agent-to-Model Mapping (Strategy Pattern)
AGENT_MODEL_MAPPING: Dict[str, str] = {
    "syntax": "fast",        # Fast model for syntax checking
    "structure": "fast",     # Fast model for structure analysis
    "domain": "powerful",    # Powerful model for domain expertise
}


def get_model_for_agent(agent_name: str) -> ModelConfig:
    """
    Get model configuration for an agent.
    
    Args:
        agent_name: Name of the agent (e.g., "syntax", "structure", "domain")
    
    Returns:
        ModelConfig for the agent (defaults to "balanced" if not mapped)
    """
    model_key = AGENT_MODEL_MAPPING.get(agent_name, "balanced")
    return MODEL_REGISTRY[model_key]


def get_all_models() -> Dict[str, ModelConfig]:
    """
    Get all available models.
    
    Returns:
        Dictionary of all model configurations
    """
    return MODEL_REGISTRY


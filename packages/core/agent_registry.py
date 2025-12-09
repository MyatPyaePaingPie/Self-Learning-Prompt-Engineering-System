"""
Agent Registry for Multi-Agent System
Factory pattern for agent creation (L:VI - Centralized Innovation)
"""

from typing import Dict, Type, List, TYPE_CHECKING
from packages.core.model_config import get_model_for_agent, ModelConfig

# Avoid circular imports
if TYPE_CHECKING:
    from packages.core.multi_agent import AgentInterface


class AgentMetadata:
    """Metadata about an agent type"""
    
    def __init__(
        self,
        name: str,
        display_name: str,
        description: str,
        focus_areas: List[str],
        model_config: ModelConfig
    ):
        self.name = name
        self.display_name = display_name
        self.description = description
        self.focus_areas = focus_areas
        self.model_config = model_config


class AgentRegistry:
    """
    Centralized registry for all agents.
    Follows factory pattern (L:VI innovation).
    
    Usage:
        # Register agent with decorator
        @register_agent("Syntax Agent", "Analyzes clarity", ["role", "clarity"])
        class SyntaxAgent(AgentInterface):
            name = "syntax"
            ...
        
        # Create agent instance
        agent = AgentRegistry.create_agent("syntax")
    """
    
    _agents: Dict[str, Type['AgentInterface']] = {}
    _metadata: Dict[str, AgentMetadata] = {}
    
    @classmethod
    def register(
        cls,
        agent_class: Type['AgentInterface'],
        display_name: str,
        description: str,
        focus_areas: List[str]
    ) -> None:
        """
        Register an agent type.
        
        Args:
            agent_class: Agent class to register
            display_name: Human-readable name
            description: Agent description
            focus_areas: List of focus areas for this agent
        """
        agent_name = agent_class.name
        model_config = get_model_for_agent(agent_name)
        
        cls._agents[agent_name] = agent_class
        cls._metadata[agent_name] = AgentMetadata(
            name=agent_name,
            display_name=display_name,
            description=description,
            focus_areas=focus_areas,
            model_config=model_config
        )
    
    @classmethod
    def create_agent(cls, agent_name: str) -> 'AgentInterface':
        """
        Create agent instance with correct model.
        
        Args:
            agent_name: Name of agent to create
        
        Returns:
            Instantiated agent with configured model
        
        Raises:
            ValueError: If agent not registered
        """
        if agent_name not in cls._agents:
            available = ", ".join(cls._agents.keys())
            raise ValueError(
                f"Unknown agent: {agent_name}. "
                f"Available agents: {available or 'none'}"
            )
        
        agent_class = cls._agents[agent_name]
        metadata = cls._metadata[agent_name]
        
        # Instantiate with model config
        return agent_class(model_config=metadata.model_config)
    
    @classmethod
    def get_all_agents(cls) -> List[str]:
        """
        Get list of all registered agent names.
        
        Returns:
            List of agent names
        """
        return list(cls._agents.keys())
    
    @classmethod
    def get_metadata(cls, agent_name: str) -> AgentMetadata:
        """
        Get agent metadata.
        
        Args:
            agent_name: Name of agent
        
        Returns:
            AgentMetadata or None if not found
        """
        return cls._metadata.get(agent_name)
    
    @classmethod
    def create_default_agents(cls) -> List['AgentInterface']:
        """
        Create default agent set (syntax, structure, domain).
        
        Returns:
            List of default agent instances
        """
        default_agents = ["syntax", "structure", "domain"]
        return [cls.create_agent(name) for name in default_agents if name in cls._agents]


def register_agent(display_name: str, description: str, focus_areas: List[str]):
    """
    Decorator to register an agent.
    
    Usage:
        @register_agent("Syntax Agent", "Analyzes clarity", ["role", "clarity"])
        class SyntaxAgent(AgentInterface):
            name = "syntax"
            ...
    
    Args:
        display_name: Human-readable name
        description: Agent description
        focus_areas: List of focus areas
    
    Returns:
        Decorator function
    """
    def decorator(agent_class: Type['AgentInterface']):
        AgentRegistry.register(agent_class, display_name, description, focus_areas)
        return agent_class
    return decorator



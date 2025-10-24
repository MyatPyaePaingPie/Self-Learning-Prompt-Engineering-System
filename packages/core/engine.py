"""
Prompt Improvement Engine for Self-Learning Prompt Engineering System
Strategic rewriting to enhance prompt clarity, specificity, and actionability
"""

import re
from typing import Dict, Any, Optional, List
from datetime import datetime


class PromptEngine:
    """
    Prompt improvement engine using template-based strategies
    Enhances prompts with role assignment, deliverables specification, and constraint handling
    """
    
    def __init__(self):
        """Initialize the prompt engine with improvement strategies"""
        self.strategies = {
            'v1': self._strategy_v1_structured,
            'v2': self._strategy_v2_enhanced,
            'template': self._strategy_template_basic
        }
    
    def improve_prompt(self, text: str, strategy: str = "v1") -> Dict[str, Any]:
        """
        Improve a prompt using the specified strategy
        
        Args:
            text: Original prompt text
            strategy: Strategy to use ('v1', 'v2', 'template')
        
        Returns:
            Dict containing improved prompt and explanation
        """
        if not text or not text.strip():
            return self._empty_improvement("Empty or whitespace-only prompt")
        
        # Get the strategy function
        strategy_func = self.strategies.get(strategy, self._strategy_v1_structured)
        
        # Apply the strategy
        return strategy_func(text)
    
    def _strategy_v1_structured(self, text: str) -> Dict[str, Any]:
        """
        Strategy V1: Template-based improvement with role assignment,
        deliverables specification, and constraint handling
        """
        
        # Detect domain from the prompt
        domain = self._detect_domain(text)
        
        # Extract task from original prompt
        task = self._extract_task(text)
        
        # Build structured prompt
        improved_parts = []
        
        # Add role
        role = f"You are a senior {domain} expert."
        improved_parts.append(role)
        
        # Add task
        task_section = f"Task: {task}"
        improved_parts.append(task_section)
        
        # Add deliverables section
        deliverables = self._generate_deliverables(domain, task)
        improved_parts.append("Deliverables:")
        for deliverable in deliverables:
            improved_parts.append(f"- {deliverable}")
        
        # Add constraints section
        constraints = self._generate_constraints(domain)
        improved_parts.append("Constraints: [time, tools, data sources]")
        
        # Add clarifying questions instruction
        clarifying = "If information is missing, list precise clarifying questions first, then proceed with best assumptions."
        improved_parts.append(clarifying)
        
        # Combine all parts
        improved_text = "\n".join(improved_parts)
        
        # Generate explanation
        explanation = self._generate_explanation_v1(text, improved_text, domain)
        
        return {
            'text': improved_text,
            'explanation': explanation,
            'strategy': 'v1',
            'domain_detected': domain,
            'timestamp': datetime.now().isoformat()
        }
    
    def _strategy_v2_enhanced(self, text: str) -> Dict[str, Any]:
        """
        Strategy V2: Enhanced version with examples and edge cases
        """
        
        # Start with V1 as base
        v1_result = self._strategy_v1_structured(text)
        
        # Add examples section
        domain = v1_result['domain_detected']
        examples = self._generate_examples(domain, text)
        
        # Enhance the prompt
        enhanced_parts = v1_result['text'].split('\n')
        
        # Insert examples before constraints
        constraint_index = next((i for i, line in enumerate(enhanced_parts) if 'Constraints:' in line), -1)
        
        if constraint_index > 0:
            example_section = ["Examples:"] + [f"- {example}" for example in examples]
            enhanced_parts = enhanced_parts[:constraint_index] + example_section + enhanced_parts[constraint_index:]
        
        enhanced_text = "\n".join(enhanced_parts)
        
        # Update explanation
        explanation = v1_result['explanation']
        explanation['bullets'].append("Added relevant examples and use cases")
        explanation['diffs'].append({
            'from': 'Basic structure',
            'to': 'Structure with examples and edge cases'
        })
        
        return {
            'text': enhanced_text,
            'explanation': explanation,
            'strategy': 'v2',
            'domain_detected': domain,
            'timestamp': datetime.now().isoformat()
        }
    
    def _strategy_template_basic(self, text: str) -> Dict[str, Any]:
        """
        Basic template strategy for simple improvements
        """
        
        # Simple template application
        if len(text.split()) < 5:
            improved = f"Please provide a detailed explanation of: {text}"
        else:
            improved = f"Task: {text}\n\nPlease provide a comprehensive response with examples and step-by-step instructions."
        
        explanation = {
            'bullets': ['Applied basic template structure', 'Added request for comprehensive response'],
            'diffs': [{'from': text, 'to': improved}]
        }
        
        return {
            'text': improved,
            'explanation': explanation,
            'strategy': 'template',
            'domain_detected': 'general',
            'timestamp': datetime.now().isoformat()
        }
    
    def _detect_domain(self, text: str) -> str:
        """Detect the domain/context of the prompt"""
        
        text_lower = text.lower()
        
        # Programming domains
        programming_keywords = ['code', 'function', 'algorithm', 'programming', 'software', 'debug', 'api', 'database']
        if any(keyword in text_lower for keyword in programming_keywords):
            if 'python' in text_lower:
                return 'Python development'
            elif any(lang in text_lower for lang in ['javascript', 'js', 'react', 'node']):
                return 'JavaScript development'
            else:
                return 'software development'
        
        # Data science
        data_keywords = ['data', 'analysis', 'machine learning', 'statistics', 'dataset', 'model']
        if any(keyword in text_lower for keyword in data_keywords):
            return 'data science'
        
        # Writing/content
        writing_keywords = ['write', 'essay', 'article', 'content', 'story', 'blog']
        if any(keyword in text_lower for keyword in writing_keywords):
            return 'content creation'
        
        # Marketing
        marketing_keywords = ['marketing', 'campaign', 'brand', 'customer', 'sales', 'promotion']
        if any(keyword in text_lower for keyword in marketing_keywords):
            return 'marketing'
        
        # Design
        design_keywords = ['design', 'ui', 'ux', 'interface', 'visual', 'layout']
        if any(keyword in text_lower for keyword in design_keywords):
            return 'design'
        
        # Default
        return 'general'
    
    def _extract_task(self, text: str) -> str:
        """Extract or refine the core task from the prompt"""
        
        # Clean up the text
        task = text.strip()
        
        # If it's already well-formed, keep it
        if len(task.split()) > 3 and any(char in task for char in '.!?'):
            return task
        
        # If it's very short, enhance it
        if len(task.split()) <= 3:
            return f"Help with {task}"
        
        return task
    
    def _generate_deliverables(self, domain: str, task: str) -> List[str]:
        """Generate appropriate deliverables based on domain"""
        
        base_deliverables = [
            "Clear, step-by-step plan",
            "Practical examples and use cases",
            "Final implementation ready to use"
        ]
        
        if 'development' in domain.lower():
            return [
                "Working code with comments and documentation",
                "Test cases and edge case handling",
                "Performance considerations and best practices"
            ]
        elif 'data' in domain.lower():
            return [
                "Data analysis methodology",
                "Visualizations and statistical insights",
                "Actionable recommendations based on findings"
            ]
        elif 'content' in domain.lower():
            return [
                "Well-structured written content",
                "Engaging tone appropriate for audience",
                "Fact-checked and properly formatted output"
            ]
        elif 'marketing' in domain.lower():
            return [
                "Strategic marketing plan with timeline",
                "Target audience analysis and messaging",
                "Measurable KPIs and success metrics"
            ]
        else:
            return base_deliverables
    
    def _generate_constraints(self, domain: str) -> List[str]:
        """Generate relevant constraints based on domain"""
        
        base_constraints = ["time limits", "available tools", "data sources"]
        
        if 'development' in domain.lower():
            return ["programming language version", "framework restrictions", "performance requirements"]
        elif 'data' in domain.lower():
            return ["data privacy requirements", "computational resources", "statistical significance levels"]
        else:
            return base_constraints
    
    def _generate_examples(self, domain: str, text: str) -> List[str]:
        """Generate relevant examples based on domain and task"""
        
        if 'development' in domain.lower():
            return [
                "Include unit tests for all functions",
                "Consider edge cases like empty inputs",
                "Optimize for readability and maintainability"
            ]
        elif 'content' in domain.lower():
            return [
                "Use active voice where possible",
                "Include relevant statistics or data",
                "Structure with clear headings and subheadings"
            ]
        else:
            return [
                "Provide concrete, actionable steps",
                "Include real-world applications",
                "Consider potential challenges and solutions"
            ]
    
    def _generate_explanation_v1(self, original: str, improved: str, domain: str) -> Dict[str, Any]:
        """Generate explanation for V1 strategy improvements"""
        
        bullets = [
            "Added explicit role for the assistant",
            "Specified deliverables and output format",
            "Inserted constraint section for clarity",
            "Required clarifying questions before solution"
        ]
        
        if domain != 'general':
            bullets.append(f"Tailored for {domain} domain")
        
        diffs = [{
            'from': original[:50] + "..." if len(original) > 50 else original,
            'to': improved[:50] + "..." if len(improved) > 50 else improved
        }]
        
        return {
            'bullets': bullets,
            'diffs': diffs,
            'improvements_made': len(bullets),
            'strategy_applied': 'Template-based structured enhancement'
        }
    
    def _empty_improvement(self, reason: str) -> Dict[str, Any]:
        """Return empty improvement result with reason"""
        return {
            'text': '',
            'explanation': {
                'bullets': [f"Cannot improve: {reason}"],
                'diffs': [],
                'improvements_made': 0,
                'strategy_applied': 'none'
            },
            'strategy': 'none',
            'domain_detected': 'unknown',
            'timestamp': datetime.now().isoformat()
        }


# Convenience function for easy integration
def improve_prompt(text: str, strategy: str = "v1") -> Dict[str, Any]:
    """
    Convenience function to improve a prompt
    
    Args:
        text: Original prompt text
        strategy: Strategy to use ('v1', 'v2', 'template')
    
    Returns:
        Improvement result dictionary
    """
    engine = PromptEngine()
    return engine.improve_prompt(text, strategy)


# Example usage and demo
if __name__ == "__main__":
    print("🚀 Prompt Engine Demo")
    print("=" * 50)
    
    # Initialize engine
    engine = PromptEngine()
    
    # Test prompts
    test_prompts = [
        "Help me code",
        "Write a Python function to sort numbers",
        "Create a marketing plan for my startup",
        "Design a user interface",
        "Analyze this data"
    ]
    
    # Test each prompt with different strategies
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n🔧 Test {i}: {prompt}")
        print("-" * 40)
        
        # Test V1 strategy
        result = engine.improve_prompt(prompt, 'v1')
        
        print(f"Domain detected: {result['domain_detected']}")
        print(f"Strategy used: {result['strategy']}")
        print("\nImproved prompt:")
        print(result['text'])
        
        print("\nExplanation:")
        for bullet in result['explanation']['bullets']:
            print(f"  • {bullet}")
    
    print("\n✅ Engine demo completed!")
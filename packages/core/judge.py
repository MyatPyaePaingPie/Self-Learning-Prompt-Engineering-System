"""
Judge System for Self-Learning Prompt Engineering System
Multi-dimensional scoring system evaluating prompts on 5 key criteria
"""

import json
import re
from typing import Dict, Any, Optional, List
from datetime import datetime


class PromptJudge:
    """
    Multi-dimensional prompt scoring system
    Evaluates prompts on: clarity, specificity, actionability, structure, context_use
    """
    
    def __init__(self):
        """Initialize the judge with scoring criteria"""
        self.criteria = {
            'clarity': {
                'weight': 1.0,
                'max_score': 10.0,
                'description': 'How clear and understandable is the prompt?'
            },
            'specificity': {
                'weight': 1.0,
                'max_score': 10.0,
                'description': 'How specific and detailed are the requirements?'
            },
            'actionability': {
                'weight': 1.0,
                'max_score': 10.0,
                'description': 'How actionable and implementable is the request?'
            },
            'structure': {
                'weight': 1.0,
                'max_score': 10.0,
                'description': 'How well-structured and organized is the prompt?'
            },
            'context_use': {
                'weight': 1.0,
                'max_score': 10.0,
                'description': 'How well does it utilize context and constraints?'
            }
        }
    
    def judge_prompt(self, text: str, rubric: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Judge a prompt across all criteria
        
        Args:
            text: The prompt text to evaluate
            rubric: Optional custom rubric (uses default if None)
        
        Returns:
            Dict with individual scores, total, and feedback
        """
        if not text or not text.strip():
            return self._empty_score("Empty or whitespace-only prompt")
        
        # Use custom rubric if provided, otherwise use default
        active_rubric = rubric if rubric else self._get_default_rubric()
        
        # Score each criterion
        scores = {}
        feedback_details = {}
        
        for criterion in self.criteria.keys():
            score, feedback = self._score_criterion(text, criterion, active_rubric)
            scores[criterion] = score
            feedback_details[criterion] = feedback
        
        # Calculate total score
        total_score = sum(scores.values())
        
        # Generate overall feedback
        overall_feedback = self._generate_overall_feedback(text, scores, feedback_details)
        
        return {
            **scores,
            'total': total_score,
            'feedback': overall_feedback,
            'timestamp': datetime.now().isoformat(),
            'rubric_used': 'default' if rubric is None else 'custom'
        }
    
    def _score_criterion(self, text: str, criterion: str, rubric: Dict) -> tuple[float, Dict[str, Any]]:
        """Score a single criterion using heuristic analysis"""
        
        if criterion == 'clarity':
            return self._score_clarity(text)
        elif criterion == 'specificity':
            return self._score_specificity(text)
        elif criterion == 'actionability':
            return self._score_actionability(text)
        elif criterion == 'structure':
            return self._score_structure(text)
        elif criterion == 'context_use':
            return self._score_context_use(text)
        else:
            return 5.0, {'reason': 'Unknown criterion', 'details': []}
    
    def _score_clarity(self, text: str) -> tuple[float, Dict[str, Any]]:
        """Score clarity based on readability and comprehension"""
        score = 5.0  # Base score
        details = []
        
        # Check for clear language indicators
        clear_indicators = ['clearly', 'specifically', 'exactly', 'precisely']
        if any(word in text.lower() for word in clear_indicators):
            score += 1.0
            details.append("Uses clarity indicators")
        
        # Check for ambiguous language
        ambiguous_words = ['maybe', 'perhaps', 'might', 'could be', 'sort of']
        if any(word in text.lower() for word in ambiguous_words):
            score -= 1.0
            details.append("Contains ambiguous language")
        
        # Check sentence structure
        sentences = text.split('.')
        avg_sentence_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
        
        if 10 <= avg_sentence_length <= 25:
            score += 0.5
            details.append("Good sentence length")
        elif avg_sentence_length > 35:
            score -= 1.0
            details.append("Sentences too long")
        
        # Check for questions vs statements balance
        question_count = text.count('?')
        statement_count = text.count('.')
        
        if question_count > 0 and statement_count > 0:
            score += 0.5
            details.append("Good balance of questions and statements")
        
        return min(max(score, 0.0), 10.0), {
            'reason': f"Clarity score based on language analysis",
            'details': details,
            'factors_analyzed': ['language_indicators', 'sentence_structure', 'question_balance']
        }
    
    def _score_specificity(self, text: str) -> tuple[float, Dict[str, Any]]:
        """Score specificity based on detail level and concrete requirements"""
        score = 5.0
        details = []
        
        # Check for specific requirements
        specific_indicators = [
            'requirements:', 'must', 'should', 'needs to', 'exactly',
            'format:', 'output:', 'deliverables:', 'constraints:'
        ]
        specificity_count = sum(1 for indicator in specific_indicators if indicator in text.lower())
        
        if specificity_count >= 3:
            score += 2.0
            details.append(f"Contains {specificity_count} specificity indicators")
        elif specificity_count >= 1:
            score += 1.0
            details.append(f"Contains {specificity_count} specificity indicator(s)")
        
        # Check for examples
        if any(word in text.lower() for word in ['example', 'for instance', 'such as', 'like']):
            score += 1.0
            details.append("Includes examples")
        
        # Check for measurements/quantities
        numbers = re.findall(r'\d+', text)
        if numbers:
            score += 0.5
            details.append("Contains specific numbers/quantities")
        
        # Check for vague language
        vague_words = ['some', 'any', 'stuff', 'things', 'something', 'anything']
        vague_count = sum(1 for word in vague_words if word in text.lower())
        if vague_count > 0:
            score -= vague_count * 0.5
            details.append(f"Contains {vague_count} vague term(s)")
        
        return min(max(score, 0.0), 10.0), {
            'reason': f"Specificity score based on detail analysis",
            'details': details,
            'factors_analyzed': ['requirement_indicators', 'examples', 'measurements', 'vague_language']
        }
    
    def _score_actionability(self, text: str) -> tuple[float, Dict[str, Any]]:
        """Score how actionable and implementable the prompt is"""
        score = 5.0
        details = []
        
        # Check for action verbs
        action_verbs = [
            'create', 'build', 'write', 'design', 'implement', 'develop',
            'generate', 'produce', 'make', 'construct', 'analyze', 'solve'
        ]
        action_count = sum(1 for verb in action_verbs if verb in text.lower())
        
        if action_count >= 2:
            score += 1.5
            details.append(f"Contains {action_count} action verbs")
        elif action_count >= 1:
            score += 1.0
            details.append(f"Contains {action_count} action verb")
        
        # Check for deliverable specification
        deliverable_indicators = ['output', 'result', 'deliverable', 'produce', 'return', 'provide']
        if any(word in text.lower() for word in deliverable_indicators):
            score += 1.0
            details.append("Specifies expected output/deliverable")
        
        # Check for step-by-step indicators
        step_indicators = ['step', 'first', 'then', 'next', 'finally', 'process']
        if any(word in text.lower() for word in step_indicators):
            score += 1.0
            details.append("Suggests step-by-step approach")
        
        # Check for tool/method specification
        if any(word in text.lower() for word in ['using', 'with', 'via', 'through']):
            score += 0.5
            details.append("Specifies tools or methods")
        
        # Penalty for overly abstract requests
        abstract_words = ['concept', 'idea', 'theory', 'philosophy', 'abstract']
        if sum(1 for word in abstract_words if word in text.lower()) > 1:
            score -= 1.0
            details.append("May be too abstract")
        
        return min(max(score, 0.0), 10.0), {
            'reason': f"Actionability score based on implementation feasibility",
            'details': details,
            'factors_analyzed': ['action_verbs', 'deliverables', 'steps', 'tools', 'abstraction_level']
        }
    
    def _score_structure(self, text: str) -> tuple[float, Dict[str, Any]]:
        """Score the organizational structure of the prompt"""
        score = 5.0
        details = []
        
        # Check for structural elements
        structural_elements = {
            'role': ['you are', 'act as', 'role:', 'as a'],
            'task': ['task:', 'objective:', 'goal:', 'need to'],
            'context': ['context:', 'background:', 'given that'],
            'constraints': ['constraint:', 'limit:', 'within', 'must not'],
            'format': ['format:', 'structure:', 'template:']
        }
        
        elements_found = []
        for element, keywords in structural_elements.items():
            if any(keyword in text.lower() for keyword in keywords):
                elements_found.append(element)
        
        # Score based on structural elements
        element_count = len(elements_found)
        if element_count >= 3:
            score += 2.0
            details.append(f"Contains {element_count} structural elements: {', '.join(elements_found)}")
        elif element_count >= 1:
            score += 1.0
            details.append(f"Contains {element_count} structural element(s): {', '.join(elements_found)}")
        
        # Check for logical flow indicators
        flow_indicators = ['first', 'then', 'next', 'finally', 'after', 'before']
        if any(word in text.lower() for word in flow_indicators):
            score += 1.0
            details.append("Shows logical flow")
        
        # Check for sectioning/organization
        if ':' in text:
            colon_count = text.count(':')
            if colon_count >= 2:
                score += 1.0
                details.append("Well-sectioned with clear categories")
        
        # Check for bullet points or numbering
        if any(char in text for char in ['•', '-', '*']) or re.search(r'\d+\.', text):
            score += 0.5
            details.append("Uses lists or bullet points")
        
        return min(max(score, 0.0), 10.0), {
            'reason': f"Structure score based on organization analysis",
            'details': details,
            'factors_analyzed': ['structural_elements', 'logical_flow', 'sectioning', 'formatting']
        }
    
    def _score_context_use(self, text: str) -> tuple[float, Dict[str, Any]]:
        """Score how well the prompt utilizes context and constraints"""
        score = 5.0
        details = []
        
        # Check for context indicators
        context_indicators = [
            'given', 'assuming', 'context', 'background', 'situation',
            'scenario', 'environment', 'setting'
        ]
        context_count = sum(1 for indicator in context_indicators if indicator in text.lower())
        
        if context_count >= 2:
            score += 1.5
            details.append(f"Rich contextual information ({context_count} indicators)")
        elif context_count >= 1:
            score += 1.0
            details.append(f"Some contextual information ({context_count} indicator)")
        
        # Check for constraint specification
        constraint_indicators = [
            'constraint', 'limit', 'restriction', 'boundary', 'within',
            'cannot', 'must not', 'avoid', 'except'
        ]
        constraint_count = sum(1 for indicator in constraint_indicators if indicator in text.lower())
        
        if constraint_count >= 2:
            score += 1.5
            details.append(f"Well-defined constraints ({constraint_count} indicators)")
        elif constraint_count >= 1:
            score += 1.0
            details.append(f"Some constraints specified ({constraint_count} indicator)")
        
        # Check for domain/expertise specification
        domain_indicators = ['expert', 'specialist', 'professional', 'experienced', 'skilled']
        if any(word in text.lower() for word in domain_indicators):
            score += 1.0
            details.append("Specifies domain expertise")
        
        # Check for audience awareness
        audience_indicators = ['for', 'audience', 'user', 'beginner', 'advanced', 'technical']
        if any(word in text.lower() for word in audience_indicators):
            score += 0.5
            details.append("Shows audience awareness")
        
        return min(max(score, 0.0), 10.0), {
            'reason': f"Context use score based on situational awareness",
            'details': details,
            'factors_analyzed': ['contextual_info', 'constraints', 'domain_specification', 'audience_awareness']
        }
    
    def _generate_overall_feedback(self, text: str, scores: Dict[str, float], feedback_details: Dict) -> Dict[str, Any]:
        """Generate comprehensive feedback based on all criteria"""
        
        # Identify strengths (scores >= 7.0)
        strengths = [criterion for criterion, score in scores.items() if score >= 7.0]
        
        # Identify weaknesses (scores < 5.0)
        weaknesses = [criterion for criterion, score in scores.items() if score < 5.0]
        
        # Generate pros
        pros = []
        for strength in strengths:
            if strength in feedback_details:
                pros.append(f"Strong {strength}: {feedback_details[strength]['reason']}")
        
        if not pros:
            pros.append("Baseline prompt structure")
        
        # Generate cons
        cons = []
        for weakness in weaknesses:
            if weakness in feedback_details:
                cons.append(f"Weak {weakness}: {feedback_details[weakness]['reason']}")
        
        # Generate summary
        total_score = sum(scores.values())
        max_possible = len(scores) * 10.0
        percentage = (total_score / max_possible) * 100
        
        if percentage >= 80:
            summary = "Excellent prompt with strong structure and clarity"
        elif percentage >= 60:
            summary = "Good prompt with room for improvement"
        elif percentage >= 40:
            summary = "Adequate prompt but needs significant enhancement"
        else:
            summary = "Prompt requires major restructuring for effectiveness"
        
        return {
            'pros': pros,
            'cons': cons if cons else ["No significant weaknesses identified"],
            'summary': summary,
            'overall_score_percentage': round(percentage, 1),
            'recommendations': self._generate_recommendations(scores, feedback_details)
        }
    
    def _generate_recommendations(self, scores: Dict[str, float], feedback_details: Dict) -> List[str]:
        """Generate actionable recommendations for improvement"""
        recommendations = []
        
        # Specific recommendations based on low scores
        for criterion, score in scores.items():
            if score < 6.0:
                if criterion == 'clarity':
                    recommendations.append("Improve clarity by using more precise language and shorter sentences")
                elif criterion == 'specificity':
                    recommendations.append("Add specific requirements, examples, or measurable outcomes")
                elif criterion == 'actionability':
                    recommendations.append("Include clear action verbs and specify expected deliverables")
                elif criterion == 'structure':
                    recommendations.append("Organize with clear sections: role, task, constraints, and format")
                elif criterion == 'context_use':
                    recommendations.append("Provide more background context and specify constraints")
        
        # General recommendations
        total_score = sum(scores.values())
        if total_score < 25:  # Less than 50% of maximum
            recommendations.append("Consider using a structured template: Role → Task → Context → Constraints → Format")
        
        return recommendations if recommendations else ["Continue refining based on specific use case"]
    
    def _empty_score(self, reason: str) -> Dict[str, Any]:
        """Return empty/zero scores with reason"""
        return {
            'clarity': 0.0,
            'specificity': 0.0,
            'actionability': 0.0,
            'structure': 0.0,
            'context_use': 0.0,
            'total': 0.0,
            'feedback': {
                'pros': [],
                'cons': [reason],
                'summary': f"Cannot score: {reason}",
                'overall_score_percentage': 0.0,
                'recommendations': ["Please provide a valid prompt text"]
            },
            'timestamp': datetime.now().isoformat(),
            'rubric_used': 'default'
        }
    
    def _get_default_rubric(self) -> Dict:
        """Get the default scoring rubric"""
        return {
            'version': '1.0',
            'description': 'Heuristic-based prompt evaluation system',
            'criteria': self.criteria,
            'scoring_method': 'heuristic'
        }


# Integration function for easy use with file storage
def judge_prompt(text: str, rubric: Optional[Dict] = None, save_to_storage: Optional[Any] = None, 
                 prompt_id: Optional[str] = None, version_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to judge a prompt and optionally save to file storage
    
    Args:
        text: Prompt text to evaluate
        rubric: Optional custom rubric
        save_to_storage: FileStorage instance to save scores to
        prompt_id: Prompt ID for file storage
        version_id: Version ID for file storage
    
    Returns:
        Judge scores dictionary
    """
    judge = PromptJudge()
    scores = judge.judge_prompt(text, rubric)
    
    # Save to file storage if provided
    if save_to_storage and prompt_id and version_id:
        try:
            save_to_storage.save_judge_scores_to_csv(prompt_id, version_id, scores)
        except Exception as e:
            print(f"⚠️  Warning: Failed to save judge scores to storage: {e}")
    
    return scores


# Example usage and demo
if __name__ == "__main__":
    print("⚖️  Prompt Judge System Demo")
    print("=" * 50)
    
    # Initialize judge
    judge = PromptJudge()
    
    # Test prompts with different quality levels
    test_prompts = [
        {
            "name": "Poor Quality Prompt",
            "text": "Help me code"
        },
        {
            "name": "Good Quality Prompt", 
            "text": """You are a senior Python developer.
Task: Write a function to calculate factorial with error handling
Requirements:
- Handle negative numbers appropriately
- Include docstring and type hints
- Provide both recursive and iterative solutions
Constraints: Python 3.8+, no external libraries
Format: Return clean, commented code with examples"""
        },
        {
            "name": "Medium Quality Prompt",
            "text": "Create a web scraper for news articles that saves data to CSV"
        }
    ]
    
    # Test each prompt
    for test_prompt in test_prompts:
        print(f"\n📝 Testing: {test_prompt['name']}")
        print("-" * 40)
        print(f"Prompt: {test_prompt['text'][:100]}...")
        
        # Get scores
        result = judge.judge_prompt(test_prompt['text'])
        
        # Display scores
        print("\n📊 Scores:")
        for criterion in ['clarity', 'specificity', 'actionability', 'structure', 'context_use']:
            print(f"  {criterion.title()}: {result[criterion]:.1f}/10.0")
        
        print(f"\nTotal Score: {result['total']:.1f}/50.0 ({result['feedback']['overall_score_percentage']:.1f}%)")
        print(f"Summary: {result['feedback']['summary']}")
        
        if result['feedback']['recommendations']:
            print("Recommendations:")
            for rec in result['feedback']['recommendations']:
                print(f"  • {rec}")
    
    print("\n✅ Judge system demo completed!")

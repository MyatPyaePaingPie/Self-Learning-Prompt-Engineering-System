"""
Security Analysis Service - Keyword-based Risk Scoring
Follows Judge service pattern (L:I Gold Standard)
"""
import logging
from dataclasses import dataclass, field
from typing import Dict, List

logger = logging.getLogger(__name__)

# Default keyword categories with weights (from master blueprint)
DEFAULT_KEYWORDS = {
    "malicious": {
        "keywords": ["hack", "exploit", "vulnerability", "inject", "bypass"],
        "weight": 15
    },
    "destructive": {
        "keywords": ["delete", "destroy", "remove", "wipe", "format"],
        "weight": 12
    },
    "privacy": {
        "keywords": ["steal", "credential", "password", "private", "sensitive"],
        "weight": 10
    },
    "system": {
        "keywords": ["root", "admin", "sudo", "privilege", "escalate"],
        "weight": 8
    }
}

@dataclass
class SecurityAssessment:
    """Risk assessment result from SecurityAnalyzer"""
    risk_score: float  # 0-100
    label: str  # safe, low-risk, medium-risk, high-risk
    is_blocked: bool  # True if risk_score >= blocking_threshold
    analysis_metadata: Dict[str, any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for database storage"""
        return {
            "risk_score": self.risk_score,
            "label": self.label,
            "is_blocked": self.is_blocked,
            "analysis_metadata": self.analysis_metadata
        }


class SecurityAnalyzer:
    """
    Keyword-based security risk analyzer
    
    Analyzes text for security risks using configurable keyword matching.
    Returns risk score (0-100), label, blocking decision, and metadata.
    
    Pattern: Follows Judge service structure (L:I)
    """
    
    def __init__(
        self,
        keywords: Dict[str, Dict] = None,
        blocking_threshold: float = 80.0
    ):
        """
        Initialize SecurityAnalyzer with configurable rules
        
        Args:
            keywords: Dict of {category: {"keywords": [...], "weight": int}}
            blocking_threshold: Risk score threshold for blocking (default: 80)
        """
        self.keywords = keywords if keywords is not None else DEFAULT_KEYWORDS
        self.blocking_threshold = blocking_threshold
        
        logger.info(
            f"SecurityAnalyzer initialized with {len(self.keywords)} categories, "
            f"blocking threshold: {blocking_threshold}"
        )
    
    def analyze(self, text: str) -> SecurityAssessment:
        """
        Analyze text for security risks
        
        Args:
            text: Input text to analyze
            
        Returns:
            SecurityAssessment with risk score, label, blocking decision, metadata
        """
        if not text or not text.strip():
            # Empty text is safe
            return SecurityAssessment(
                risk_score=0.0,
                label="safe",
                is_blocked=False,
                analysis_metadata={
                    "matched_keywords": {},
                    "risk_breakdown": {},
                    "total_matches": 0
                }
            )
        
        # Calculate risk score
        risk_score, metadata = self._calculate_risk_score(text)
        
        # Determine label
        label = self._determine_label(risk_score)
        
        # Check if should block
        is_blocked = self._should_block(risk_score)
        
        logger.debug(
            f"SecurityAnalyzer: risk_score={risk_score:.1f}, label={label}, "
            f"is_blocked={is_blocked}, matches={metadata['total_matches']}"
        )
        
        return SecurityAssessment(
            risk_score=risk_score,
            label=label,
            is_blocked=is_blocked,
            analysis_metadata=metadata
        )
    
    def _calculate_risk_score(self, text: str) -> tuple[float, Dict]:
        """
        Calculate risk score using keyword matching
        
        Algorithm (from master blueprint):
        - Risk Score = Σ(keyword_weight * keyword_count)
        - Cap at 100, floor at 0
        - Case-insensitive matching
        
        Args:
            text: Input text
            
        Returns:
            Tuple of (risk_score, metadata)
        """
        text_lower = text.lower()
        
        matched_keywords = {}
        risk_breakdown = {}
        total_score = 0.0
        total_matches = 0
        
        # Scan each category
        for category, config in self.keywords.items():
            keywords = config["keywords"]
            weight = config["weight"]
            
            # Find matched keywords in this category
            category_matches = []
            category_count = 0
            
            for keyword in keywords:
                count = text_lower.count(keyword.lower())
                if count > 0:
                    category_matches.append(keyword)
                    category_count += count
            
            # Calculate category contribution
            if category_matches:
                matched_keywords[category] = category_matches
                category_score = weight * category_count
                risk_breakdown[category] = category_score
                total_score += category_score
                total_matches += category_count
        
        # Cap at 100, floor at 0
        risk_score = max(0.0, min(100.0, total_score))
        
        metadata = {
            "matched_keywords": matched_keywords,
            "risk_breakdown": risk_breakdown,
            "total_matches": total_matches
        }
        
        return risk_score, metadata
    
    def _determine_label(self, risk_score: float) -> str:
        """
        Determine label from risk score
        
        Label mapping (from master blueprint):
        - 0-20: "safe"
        - 21-40: "low-risk"
        - 41-70: "medium-risk"
        - 71-100: "high-risk"
        
        Args:
            risk_score: Risk score (0-100)
            
        Returns:
            Label string
        """
        if risk_score <= 20:
            return "safe"
        elif risk_score <= 40:
            return "low-risk"
        elif risk_score <= 70:
            return "medium-risk"
        else:
            return "high-risk"
    
    def _should_block(self, risk_score: float) -> bool:
        """
        Determine if input should be blocked
        
        Blocking rule (from master blueprint):
        - If risk_score >= blocking_threshold → is_blocked=True
        
        Args:
            risk_score: Risk score (0-100)
            
        Returns:
            True if should block, False otherwise
        """
        return risk_score >= self.blocking_threshold



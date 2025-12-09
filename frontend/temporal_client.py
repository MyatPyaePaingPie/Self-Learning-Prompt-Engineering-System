import requests
from typing import Optional, Dict, Any, List
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

class TemporalClient:
    """
    Client for temporal analysis API endpoints.
    Week 12: Temporal Prompt Learning & Causal Analysis
    
    Pattern: Follows auth_client.py pattern (requests-based, error handling)
    """
    
    def __init__(self, base_url: str = None, token: str = None):
        """
        Initialize temporal client.
        
        Args:
            base_url: API base URL (default from env or localhost:8001)
            token: Authentication token for API calls
        """
        self.base_url = base_url or os.getenv("API_BASE_URL", "http://localhost:8001")
        self.token = token
        self.session = requests.Session()
        
        # Add security headers
        self.session.headers.update({
            'User-Agent': 'TemporalClient/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        
        # Add auth token if provided
        if self.token:
            self.session.headers.update({
                'Authorization': f'Bearer {self.token}'
            })
    
    def get_timeline(
        self, 
        prompt_id: str, 
        start_date: Optional[str] = None, 
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get temporal timeline of prompt versions with scores.
        
        Args:
            prompt_id: UUID of the prompt
            start_date: Start date (ISO 8601 format, optional)
            end_date: End date (ISO 8601 format, optional)
            
        Returns:
            Dict with success flag and data/error:
            {
                "success": True,
                "data": [
                    {
                        "timestamp": "2025-12-03T10:00:00Z",
                        "score": 75.5,
                        "version_id": "uuid",
                        "change_type": "wording"
                    },
                    ...
                ]
            }
        """
        try:
            # Default to last 30 days if no dates provided
            if not start_date:
                start_date = (datetime.now() - timedelta(days=30)).isoformat()
            if not end_date:
                end_date = datetime.now().isoformat()
            
            params = {
                "prompt_id": prompt_id,
                "start": start_date,
                "end": end_date
            }
            
            response = self.session.get(
                f"{self.base_url}/api/temporal/timeline",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            elif response.status_code == 404:
                return {"success": False, "error": "Prompt not found"}
            else:
                return {"success": False, "error": response.json().get("detail", "Failed to get timeline")}
                
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"Connection error: {str(e)}"}
    
    def get_statistics(self, prompt_id: str) -> Dict[str, Any]:
        """
        Get temporal statistics for prompt evolution.
        
        Args:
            prompt_id: UUID of the prompt
            
        Returns:
            Dict with success flag and data/error:
            {
                "success": True,
                "data": {
                    "trend": "improving",  # "improving" | "degrading" | "stable"
                    "avg_score": 75.5,
                    "score_std": 5.2,
                    "total_versions": 60,
                    "min_score": 60.0,
                    "max_score": 85.0
                }
            }
        """
        try:
            params = {"prompt_id": prompt_id}
            
            response = self.session.get(
                f"{self.base_url}/api/temporal/statistics",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            elif response.status_code == 404:
                return {"success": False, "error": "Prompt not found"}
            else:
                return {"success": False, "error": response.json().get("detail", "Failed to get statistics")}
                
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"Connection error: {str(e)}"}
    
    def get_causal_hints(self, prompt_id: str) -> Dict[str, Any]:
        """
        Get causal hints showing correlation between change types and score deltas.
        
        Args:
            prompt_id: UUID of the prompt
            
        Returns:
            Dict with success flag and data/error:
            {
                "success": True,
                "data": [
                    {
                        "change_type": "structure",
                        "avg_score_delta": 5.2,
                        "occurrence_count": 15
                    },
                    ...
                ]
            }
        """
        try:
            params = {"prompt_id": prompt_id}
            
            response = self.session.get(
                f"{self.base_url}/api/temporal/causal-hints",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            elif response.status_code == 404:
                return {"success": False, "error": "Prompt not found"}
            else:
                return {"success": False, "error": response.json().get("detail", "Failed to get causal hints")}
                
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"Connection error: {str(e)}"}
    
    def generate_synthetic(
        self, 
        prompt_id: str, 
        days: int = 30, 
        versions_per_day: int = 2
    ) -> Dict[str, Any]:
        """
        Generate synthetic prompt version history for testing.
        
        Args:
            prompt_id: UUID of the prompt
            days: Number of days of history (default 30)
            versions_per_day: Versions per day (default 2)
            
        Returns:
            Dict with success flag and data/error:
            {
                "success": True,
                "data": {
                    "created_versions": 60,
                    "prompt_id": "uuid",
                    "days": 30,
                    "versions_per_day": 2
                }
            }
        """
        try:
            payload = {
                "prompt_id": prompt_id,
                "days": days,
                "versions_per_day": versions_per_day
            }
            
            response = self.session.post(
                f"{self.base_url}/api/temporal/generate-synthetic",
                json=payload,
                timeout=30  # Longer timeout for generation
            )
            
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            elif response.status_code == 404:
                return {"success": False, "error": "Prompt not found"}
            else:
                return {"success": False, "error": response.json().get("detail", "Failed to generate synthetic data")}
                
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"Connection error: {str(e)}"}
    
    def get_all_prompts(self) -> Dict[str, Any]:
        """
        Get list of all prompts for selection dropdown.
        
        Note: This is a helper method - actual implementation depends on
        existing prompts API structure.
        
        Returns:
            Dict with success flag and data/error
        """
        try:
            response = self.session.get(
                f"{self.base_url}/v1/prompts",
                timeout=10
            )
            
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": "Failed to get prompts"}
                
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"Connection error: {str(e)}"}


def init_temporal_client(token: str = None) -> TemporalClient:
    """
    Initialize temporal client with optional authentication token.
    
    Args:
        token: Authentication token (from session state)
        
    Returns:
        TemporalClient instance
    """
    return TemporalClient(token=token)



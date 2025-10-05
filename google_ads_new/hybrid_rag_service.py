"""
Hybrid RAG Service that combines documentation knowledge with actual Google Ads API calls
"""

import logging
from typing import Dict, Any, List, Optional
from django.http import JsonResponse
from .rag_client import get_rag_client
from .google_ads_api_service import GoogleAdsAPIService
from .models import GoogleAdsAccount, GoogleAdsCampaign, GoogleAdsAdGroup

logger = logging.getLogger(__name__)

class HybridRAGService:
    """Service that combines RAG knowledge with actual Google Ads API calls"""
    
    def __init__(self):
        self.rag_client = get_rag_client()
        self.api_service = GoogleAdsAPIService()
    
    def process_query(self, query: str, user_id: int = None, customer_id: str = None) -> Dict[str, Any]:
        """
        Process a query that can combine RAG knowledge with actual API calls
        
        Args:
            query: The user's question
            user_id: User ID for authentication
            customer_id: Google Ads customer ID for API calls
        """
        try:
            # First, get RAG knowledge about the query
            rag_response = self.rag_client.query(query)
            
            # Determine if this query requires actual API data
            requires_api_data = self._requires_api_data(query)
            
            if requires_api_data and customer_id:
                # Get actual data from Google Ads API
                api_data = self._get_api_data(query, customer_id)
                
                # Combine RAG knowledge with actual data
                combined_response = self._combine_responses(rag_response, api_data, query)
                return combined_response
            else:
                # Return only RAG knowledge
                return {
                    "answer": rag_response["answer"],
                    "sources": rag_response["sources"],
                    "query": query,
                    "success": True,
                    "data_type": "documentation_only",
                    "note": "This response is based on Google Ads API documentation. To get actual data from your account, please provide a customer ID."
                }
                
        except Exception as e:
            logger.error(f"Error in hybrid RAG service: {e}")
            return {
                "answer": f"Sorry, I encountered an error: {str(e)}",
                "sources": [],
                "query": query,
                "success": False,
                "error": str(e)
            }
    
    def _requires_api_data(self, query: str) -> bool:
        """Determine if the query requires actual API data"""
        api_keywords = [
            "my campaigns", "my ad groups", "my keywords", "my account",
            "show me", "list", "get", "retrieve", "fetch",
            "campaigns in my account", "ad groups in my account",
            "performance data", "metrics", "statistics"
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in api_keywords)
    
    def _get_api_data(self, query: str, customer_id: str) -> Dict[str, Any]:
        """Get actual data from Google Ads API based on the query"""
        try:
            query_lower = query.lower()
            
            if "campaign" in query_lower:
                return self._get_campaigns_data(customer_id)
            elif "ad group" in query_lower:
                return self._get_ad_groups_data(customer_id)
            elif "keyword" in query_lower:
                return self._get_keywords_data(customer_id)
            elif "account" in query_lower:
                return self._get_account_data(customer_id)
            else:
                return {"data": [], "message": "No specific data type identified"}
                
        except Exception as e:
            logger.error(f"Error getting API data: {e}")
            return {"data": [], "error": str(e)}
    
    def _get_campaigns_data(self, customer_id: str) -> Dict[str, Any]:
        """Get campaigns data from API"""
        try:
            # Use your existing API service
            campaigns = self.api_service.get_campaigns(customer_id)
            return {
                "data": campaigns,
                "data_type": "campaigns",
                "count": len(campaigns) if campaigns else 0
            }
        except Exception as e:
            return {"data": [], "error": str(e)}
    
    def _get_ad_groups_data(self, customer_id: str) -> Dict[str, Any]:
        """Get ad groups data from API"""
        try:
            ad_groups = self.api_service.get_ad_groups(customer_id)
            return {
                "data": ad_groups,
                "data_type": "ad_groups",
                "count": len(ad_groups) if ad_groups else 0
            }
        except Exception as e:
            return {"data": [], "error": str(e)}
    
    def _get_keywords_data(self, customer_id: str) -> Dict[str, Any]:
        """Get keywords data from API"""
        try:
            keywords = self.api_service.get_keywords(customer_id)
            return {
                "data": keywords,
                "data_type": "keywords",
                "count": len(keywords) if keywords else 0
            }
        except Exception as e:
            return {"data": [], "error": str(e)}
    
    def _get_account_data(self, customer_id: str) -> Dict[str, Any]:
        """Get account data from API"""
        try:
            account_info = self.api_service.get_account_info(customer_id)
            return {
                "data": account_info,
                "data_type": "account",
                "count": 1 if account_info else 0
            }
        except Exception as e:
            return {"data": [], "error": str(e)}
    
    def _combine_responses(self, rag_response: Dict[str, Any], api_data: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Combine RAG knowledge with actual API data"""
        
        # Create a comprehensive response
        combined_answer = f"""
{rag_response['answer']}

## Your Account Data:

Based on your query "{query}", here's the actual data from your Google Ads account:

"""
        
        if api_data.get("data"):
            if api_data["data_type"] == "campaigns":
                combined_answer += f"**Campaigns ({api_data['count']} found):**\n"
                for campaign in api_data["data"][:5]:  # Show first 5
                    combined_answer += f"- {campaign.get('name', 'N/A')} (ID: {campaign.get('id', 'N/A')})\n"
                if api_data['count'] > 5:
                    combined_answer += f"... and {api_data['count'] - 5} more campaigns\n"
                    
            elif api_data["data_type"] == "ad_groups":
                combined_answer += f"**Ad Groups ({api_data['count']} found):**\n"
                for ad_group in api_data["data"][:5]:
                    combined_answer += f"- {ad_group.get('name', 'N/A')} (ID: {ad_group.get('id', 'N/A')})\n"
                if api_data['count'] > 5:
                    combined_answer += f"... and {api_data['count'] - 5} more ad groups\n"
                    
            elif api_data["data_type"] == "keywords":
                combined_answer += f"**Keywords ({api_data['count']} found):**\n"
                for keyword in api_data["data"][:5]:
                    combined_answer += f"- {keyword.get('text', 'N/A')} (Match Type: {keyword.get('match_type', 'N/A')})\n"
                if api_data['count'] > 5:
                    combined_answer += f"... and {api_data['count'] - 5} more keywords\n"
        else:
            combined_answer += "No data found in your account for this query.\n"
        
        return {
            "answer": combined_answer,
            "sources": rag_response["sources"],
            "api_data": api_data,
            "query": query,
            "success": True,
            "data_type": "hybrid",
            "note": "This response combines documentation knowledge with your actual account data."
        }

# Global instance
_hybrid_service = None

def get_hybrid_service():
    """Get the global hybrid RAG service instance"""
    global _hybrid_service
    if _hybrid_service is None:
        _hybrid_service = HybridRAGService()
    return _hybrid_service


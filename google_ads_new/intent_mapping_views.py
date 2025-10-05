"""
Intent Mapping API Views
API endpoints for mapping user queries to intent actions
"""

import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse

from .intent_mapping_service import get_intent_mapping_service

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def map_query_to_intents(request):
    """
    Map user query to intent actions with date ranges and filters
    
    POST /google-ads-new/api/intent-mapping/
    
    Body:
    {
        "query": "Show me campaigns with status active from last 7 days",
        "user_context": {
            "customer_id": "1234567890",
            "campaigns": ["campaign1", "campaign2"]
        }
    }
    
    Response:
    {
        "success": true,
        "actions": ["GET_CAMPAIGNS_WITH_FILTERS"],
        "date_range": {
            "start_date": "2024-01-08",
            "end_date": "2024-01-15",
            "period": "last_7_days"
        },
        "filters": [
            {
                "field": "status",
                "operator": "equals",
                "value": "ACTIVE",
                "description": "Campaigns with active status"
            }
        ],
        "confidence": 0.95,
        "reasoning": "Query matches campaign filtering request with date range and status filter",
        "parameters": {
            "limit": 50,
            "sort_by": "clicks",
            "order": "desc"
        }
    }
    """
    try:
        data = request.data
        query = data.get('query', '').strip()
        user_context = data.get('user_context', {})
        
        if not query:
            return Response({
                "success": False,
                "error": "Query is required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get intent mapping service
        intent_service = get_intent_mapping_service()
        
        # Map query to intents
        result = intent_service.map_query_to_intents(query, user_context)
        
        return Response({
            "success": True,
            **result.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Error in intent mapping: {e}")
        return Response({
            "success": False,
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_available_actions(request):
    """
    Get all available intent actions
    
    GET /google-ads-new/api/intent-mapping/actions/
    
    Response:
    {
        "success": true,
        "actions": [
            {
                "action": "GET_CAMPAIGNS",
                "description": "Retrieve campaign information",
                "category": "basic_operations",
                "requires_auth": true,
                "keywords": ["campaigns", "campaign", "list campaigns"]
            },
            ...
        ],
        "categories": {
            "basic_operations": 15,
            "analysis": 8,
            ...
        }
    }
    """
    try:
        intent_service = get_intent_mapping_service()
        
        # Get all actions
        actions = intent_service.intent_actions
        
        # Count by category
        categories = {}
        for action in actions:
            category = action['category']
            categories[category] = categories.get(category, 0) + 1
        
        return Response({
            "success": True,
            "actions": actions,
            "categories": categories,
            "total_actions": len(actions)
        })
        
    except Exception as e:
        logger.error(f"Error getting available actions: {e}")
        return Response({
            "success": False,
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_actions_by_category(request, category):
    """
    Get actions by category
    
    GET /google-ads-new/api/intent-mapping/actions/{category}/
    
    Response:
    {
        "success": true,
        "category": "basic_operations",
        "actions": ["GET_CAMPAIGNS", "GET_ADS", ...],
        "count": 15
    }
    """
    try:
        intent_service = get_intent_mapping_service()
        
        # Get actions by category
        actions = intent_service.get_actions_by_category(category)
        
        if not actions:
            return Response({
                "success": False,
                "error": f"Category '{category}' not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            "success": True,
            "category": category,
            "actions": actions,
            "count": len(actions)
        })
        
    except Exception as e:
        logger.error(f"Error getting actions by category: {e}")
        return Response({
            "success": False,
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_action_details(request, action_name):
    """
    Get details for a specific action
    
    GET /google-ads-new/api/intent-mapping/actions/{action_name}/
    
    Response:
    {
        "success": true,
        "action": {
            "action": "GET_CAMPAIGNS",
            "description": "Retrieve campaign information",
            "category": "basic_operations",
            "requires_auth": true,
            "keywords": ["campaigns", "campaign", "list campaigns"]
        }
    }
    """
    try:
        intent_service = get_intent_mapping_service()
        
        # Get action details
        action_details = intent_service.get_action_details(action_name)
        
        if not action_details:
            return Response({
                "success": False,
                "error": f"Action '{action_name}' not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            "success": True,
            "action": action_details
        })
        
    except Exception as e:
        logger.error(f"Error getting action details: {e}")
        return Response({
            "success": False,
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def extract_date_range(request):
    """
    Extract date range from query using pattern matching
    
    POST /google-ads-new/api/intent-mapping/extract-date-range/
    
    Body:
    {
        "query": "Show me data from last 7 days"
    }
    
    Response:
    {
        "success": true,
        "date_range": {
            "start_date": "2024-01-08",
            "end_date": "2024-01-15",
            "period": "last_7_days"
        }
    }
    """
    try:
        data = request.data
        query = data.get('query', '').strip()
        
        if not query:
            return Response({
                "success": False,
                "error": "Query is required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        intent_service = get_intent_mapping_service()
        
        # Extract date ranges
        date_ranges = intent_service.extract_date_range_from_query(query)
        
        return Response({
            "success": True,
            "date_ranges": [dr.to_dict() for dr in date_ranges]
        })
        
    except Exception as e:
        logger.error(f"Error extracting date range: {e}")
        return Response({
            "success": False,
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def test_intent_mapping(request):
    """
    Test intent mapping with sample queries (no auth required for testing)
    
    POST /google-ads-new/api/intent-mapping/test/
    
    Body:
    {
        "query": "Show me active campaigns from last 30 days with budget > $100"
    }
    """
    try:
        data = request.data
        query = data.get('query', '').strip()
        
        if not query:
            return Response({
                "success": False,
                "error": "Query is required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        intent_service = get_intent_mapping_service()
        
        # Map query to intents
        result = intent_service.map_query_to_intents(query)
        
        return Response({
            "success": True,
            "query": query,
            **result.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Error in test intent mapping: {e}")
        return Response({
            "success": False,
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

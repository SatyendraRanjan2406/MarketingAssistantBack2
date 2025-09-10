"""
Django views for Google Ads RAG system
"""

import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .rag_client import get_rag_client, initialize_rag_client
from .document_scraper import scrape_google_ads_docs
from .vector_store import setup_vector_store

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["POST"])
def query_rag(request):
    """Query the RAG system"""
    try:
        # Parse request body
        body = json.loads(request.body)
        query = body.get("query", "").strip()
        
        if not query:
            return JsonResponse({
                "success": False,
                "error": "Query is required"
            }, status=400)
        
        # Get RAG client and process query
        rag_client = get_rag_client()
        result = rag_client.query(query)
        
        return JsonResponse(result)
        
    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "error": "Invalid JSON in request body"
        }, status=400)
    except Exception as e:
        logger.error(f"Error in query_rag: {e}")
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def search_documents(request):
    """Search for similar documents without generating an answer"""
    try:
        body = json.loads(request.body)
        query = body.get("query", "").strip()
        limit = body.get("limit", 5)
        
        if not query:
            return JsonResponse({
                "success": False,
                "error": "Query is required"
            }, status=400)
        
        rag_client = get_rag_client()
        similar_docs = rag_client.get_similar_docs(query, limit=limit)
        
        return JsonResponse({
            "success": True,
            "query": query,
            "documents": similar_docs,
            "count": len(similar_docs)
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "error": "Invalid JSON in request body"
        }, status=400)
    except Exception as e:
        logger.error(f"Error in search_documents: {e}")
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def rag_status(request):
    """Get RAG system status and statistics"""
    try:
        rag_client = get_rag_client()
        stats = rag_client.get_collection_stats()
        
        return JsonResponse({
            "success": True,
            "status": "active",
            "collection_stats": stats
        })
        
    except Exception as e:
        logger.error(f"Error in rag_status: {e}")
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def rebuild_vector_store(request):
    """Rebuild the vector store with fresh data"""
    try:
        # Check if user is authenticated (optional)
        if not request.user.is_authenticated:
            return JsonResponse({
                "success": False,
                "error": "Authentication required"
            }, status=401)
        
        # Scrape documents
        logger.info("Starting document scraping...")
        documents = scrape_google_ads_docs()
        
        if not documents:
            return JsonResponse({
                "success": False,
                "error": "No documents were scraped"
            }, status=500)
        
        # Setup vector store
        logger.info("Setting up vector store...")
        vector_store = setup_vector_store(documents, recreate=True)
        
        # Reinitialize RAG client
        initialize_rag_client()
        
        return JsonResponse({
            "success": True,
            "message": f"Vector store rebuilt with {len(documents)} document chunks",
            "documents_count": len(documents)
        })
        
    except Exception as e:
        logger.error(f"Error in rebuild_vector_store: {e}")
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)

# REST API views using Django REST Framework
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_query_rag(request):
    """REST API endpoint for RAG queries"""
    try:
        query = request.data.get("query", "").strip()
        
        if not query:
            return Response({
                "success": False,
                "error": "Query is required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        rag_client = get_rag_client()
        result = rag_client.query(query)
        
        return Response(result)
        
    except Exception as e:
        logger.error(f"Error in api_query_rag: {e}")
        return Response({
            "success": False,
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_rag_status(request):
    """REST API endpoint for RAG status"""
    try:
        rag_client = get_rag_client()
        stats = rag_client.get_collection_stats()
        
        return Response({
            "success": True,
            "status": "active",
            "collection_stats": stats
        })
        
    except Exception as e:
        logger.error(f"Error in api_rag_status: {e}")
        return Response({
            "success": False,
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_search_documents(request):
    """REST API endpoint for document search"""
    try:
        query = request.data.get("query", "").strip()
        limit = request.data.get("limit", 5)
        
        if not query:
            return Response({
                "success": False,
                "error": "Query is required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        rag_client = get_rag_client()
        similar_docs = rag_client.get_similar_docs(query, limit=limit)
        
        return Response({
            "success": True,
            "query": query,
            "documents": similar_docs,
            "count": len(similar_docs)
        })
        
    except Exception as e:
        logger.error(f"Error in api_search_documents: {e}")
        return Response({
            "success": False,
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

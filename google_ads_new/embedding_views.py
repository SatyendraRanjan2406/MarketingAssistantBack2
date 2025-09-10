"""
Django views for viewing Qdrant embeddings
"""

import os
import sys
import django
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

def embedding_dashboard(request):
    """Main dashboard for viewing embeddings"""
    try:
        from qdrant_client import QdrantClient
        
        # Connect to Qdrant
        client = QdrantClient("localhost", port=6333)
        
        # Get collection info
        collection_info = client.get_collection("google_ads_docs")
        
        # Get sample points
        points = client.scroll(
            collection_name="google_ads_docs",
            limit=10,
            with_payload=True,
            with_vectors=True
        )
        
        # Process sample embeddings
        sample_embeddings = []
        for point in points[0]:
            sample_embeddings.append({
                'id': point.id,
                'source': point.payload.get('source', 'Unknown'),
                'text': point.payload.get('text', ''),
                'chunk': point.payload.get('chunk', 0),
                'total_chunks': point.payload.get('total_chunks', 0),
                'section': point.payload.get('section', 'general'),
                'vector_preview': str(point.vector[:10]) + '...'
            })
        
        # Group by source
        sources = {}
        for point in points[0]:
            source = point.payload.get('source', 'Unknown')
            sources[source] = sources.get(source, 0) + 1
        
        context = {
            'collection_name': 'google_ads_docs',
            'points_count': collection_info.points_count,
            'vector_size': collection_info.config.params.vectors.size,
            'distance_metric': collection_info.config.params.vectors.distance,
            'sources': sources,
            'sample_embeddings': sample_embeddings,
            'sample_count': len(sample_embeddings)
        }
        
        return render(request, 'google_ads_new/embedding_dashboard.html', context)
        
    except Exception as e:
        context = {'error': str(e)}
        return render(request, 'google_ads_new/embedding_dashboard.html', context)

@csrf_exempt
@require_http_methods(["POST"])
def search_embeddings(request):
    """Search embeddings via AJAX"""
    try:
        data = json.loads(request.body)
        query = data.get('query', '')
        
        from google_ads_new.rag_client import get_rag_client
        
        rag_client = get_rag_client()
        results = rag_client.get_similar_docs(query, limit=5)
        
        return JsonResponse({
            'success': True,
            'documents': results
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

def embedding_stats(request):
    """Get embedding statistics as JSON"""
    try:
        from qdrant_client import QdrantClient
        
        client = QdrantClient("localhost", port=6333)
        
        # Get collection info
        collection_info = client.get_collection("google_ads_docs")
        
        # Get all points for source analysis
        points = client.scroll(
            collection_name="google_ads_docs",
            limit=1000,  # Get more points for better analysis
            with_payload=True,
            with_vectors=False
        )
        
        # Group by source URL
        sources = {}
        for point in points[0]:
            source = point.payload.get('source', 'Unknown')
            if source not in sources:
                sources[source] = 0
            sources[source] += 1
        
        return JsonResponse({
            'success': True,
            'collection_name': 'google_ads_docs',
            'points_count': collection_info.points_count,
            'vector_size': collection_info.config.params.vectors.size,
            'distance_metric': collection_info.config.params.vectors.distance,
            'sources': sources,
            'total_sources': len(sources)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

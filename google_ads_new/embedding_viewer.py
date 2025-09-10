#!/usr/bin/env python3
"""
Simple web interface to view Qdrant embeddings
"""

import os
import sys
import django
from flask import Flask, render_template_string, jsonify, request
import json

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketing_assistant_project.settings')
django.setup()

app = Flask(__name__)

# HTML template for the embedding viewer
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Qdrant Embeddings Viewer</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: #f0f0f0; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
        .stats { display: flex; gap: 20px; margin: 20px 0; }
        .stat-box { background: #e8f4fd; padding: 15px; border-radius: 5px; flex: 1; }
        .embedding-item { border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }
        .source { color: #0066cc; font-weight: bold; }
        .text { margin: 10px 0; }
        .metadata { font-size: 0.9em; color: #666; }
        .vector-preview { font-family: monospace; font-size: 0.8em; color: #666; }
        .search-box { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; }
        .search-results { margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 Qdrant Embeddings Viewer</h1>
            <p>View and search embeddings stored in Qdrant vector database</p>
        </div>
        
        <div class="stats">
            <div class="stat-box">
                <h3>Collection Info</h3>
                <p><strong>Name:</strong> {{ collection_name }}</p>
                <p><strong>Points:</strong> {{ points_count }}</p>
                <p><strong>Vector Size:</strong> {{ vector_size }}</p>
                <p><strong>Distance:</strong> {{ distance_metric }}</p>
            </div>
            <div class="stat-box">
                <h3>Sources</h3>
                {% for source, count in sources.items() %}
                <p><strong>{{ source.split('/')[-1] }}:</strong> {{ count }} chunks</p>
                {% endfor %}
            </div>
        </div>
        
        <div>
            <h3>Search Embeddings</h3>
            <input type="text" class="search-box" id="searchInput" placeholder="Search for similar content...">
            <button onclick="searchEmbeddings()">Search</button>
        </div>
        
        <div id="searchResults" class="search-results"></div>
        
        <div>
            <h3>Sample Embeddings ({{ sample_count }} shown)</h3>
            {% for embedding in sample_embeddings %}
            <div class="embedding-item">
                <div class="source">{{ embedding.source }}</div>
                <div class="text">{{ embedding.text[:200] }}{% if embedding.text|length > 200 %}...{% endif %}</div>
                <div class="metadata">
                    <strong>Chunk:</strong> {{ embedding.chunk }}/{{ embedding.total_chunks }} | 
                    <strong>Section:</strong> {{ embedding.section }} | 
                    <strong>Vector ID:</strong> {{ embedding.id }}
                </div>
                <div class="vector-preview">
                    <strong>Vector (first 10 dims):</strong> {{ embedding.vector_preview }}
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
    
    <script>
        async function searchEmbeddings() {
            const query = document.getElementById('searchInput').value;
            if (!query) return;
            
            const resultsDiv = document.getElementById('searchResults');
            resultsDiv.innerHTML = '<p>Searching...</p>';
            
            try {
                const response = await fetch('/search', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({query: query})
                });
                
                const data = await response.json();
                
                let html = '<h3>Search Results</h3>';
                if (data.success && data.documents) {
                    data.documents.forEach((doc, i) => {
                        html += `
                            <div class="embedding-item">
                                <div class="source">${doc.source || 'Unknown'}</div>
                                <div class="text">${doc.text.substring(0, 200)}${doc.text.length > 200 ? '...' : ''}</div>
                                <div class="metadata">Chunk: ${doc.chunk} | Section: ${doc.section}</div>
                            </div>
                        `;
                    });
                } else {
                    html += '<p>No results found or error occurred.</p>';
                }
                
                resultsDiv.innerHTML = html;
            } catch (error) {
                resultsDiv.innerHTML = '<p>Error searching: ' + error.message + '</p>';
            }
        }
    </script>
</body>
</html>
"""

def get_qdrant_data():
    """Get data from Qdrant"""
    try:
        from qdrant_client import QdrantClient
        
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
        
        return {
            'collection_name': 'google_ads_docs',
            'points_count': collection_info.points_count,
            'vector_size': collection_info.config.params.vectors.size,
            'distance_metric': collection_info.config.params.vectors.distance,
            'sources': sources,
            'sample_embeddings': sample_embeddings,
            'sample_count': len(sample_embeddings)
        }
        
    except Exception as e:
        return {'error': str(e)}

@app.route('/')
def index():
    """Main page"""
    data = get_qdrant_data()
    return render_template_string(HTML_TEMPLATE, **data)

@app.route('/search', methods=['POST'])
def search():
    """Search embeddings"""
    try:
        from google_ads_new.rag_client import get_rag_client
        
        data = request.get_json()
        query = data.get('query', '')
        
        rag_client = get_rag_client()
        results = rag_client.get_similar_docs(query, limit=5)
        
        return jsonify({
            'success': True,
            'documents': results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    print("Starting Embedding Viewer...")
    print("Open: http://localhost:5000")
    app.run(debug=True, port=5000)

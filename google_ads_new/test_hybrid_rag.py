#!/usr/bin/env python3
"""
Test script to demonstrate the difference between RAG and Hybrid RAG
"""

import os
import sys
import django

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketing_assistant_project.settings')
django.setup()

from google_ads_new.rag_client import get_rag_client
from google_ads_new.hybrid_rag_service import get_hybrid_service

def test_rag_vs_hybrid():
    print("🔍 Testing RAG vs Hybrid RAG")
    print("=" * 60)
    
    # Test queries
    queries = [
        "How do I create a campaign?",
        "Show me my campaigns",
        "What is OAuth authentication?",
        "List my ad groups"
    ]
    
    rag_client = get_rag_client()
    hybrid_service = get_hybrid_service()
    
    for query in queries:
        print(f"\n📝 Query: '{query}'")
        print("-" * 40)
        
        # Test regular RAG
        print("🤖 Regular RAG Response:")
        rag_response = rag_client.query(query)
        print(f"   Answer: {rag_response['answer'][:200]}...")
        print(f"   Sources: {len(rag_response['sources'])} found")
        print(f"   Data Type: Documentation only")
        
        # Test hybrid RAG (without customer ID)
        print("\n🔗 Hybrid RAG Response (no customer ID):")
        hybrid_response = hybrid_service.process_query(query, user_id=1, customer_id="")
        print(f"   Answer: {hybrid_response['answer'][:200]}...")
        print(f"   Data Type: {hybrid_response.get('data_type', 'unknown')}")
        print(f"   Note: {hybrid_response.get('note', 'N/A')}")
        
        # Test hybrid RAG (with customer ID)
        print("\n🔗 Hybrid RAG Response (with customer ID):")
        hybrid_response_with_data = hybrid_service.process_query(query, user_id=1, customer_id="1234567890")
        print(f"   Answer: {hybrid_response_with_data['answer'][:200]}...")
        print(f"   Data Type: {hybrid_response_with_data.get('data_type', 'unknown')}")
        print(f"   API Data: {hybrid_response_with_data.get('api_data', {}).get('data_type', 'N/A')}")
        
        print("\n" + "="*60)

if __name__ == "__main__":
    test_rag_vs_hybrid()


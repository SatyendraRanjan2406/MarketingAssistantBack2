# RAG System cURL Examples

Complete cURL examples for testing the Google Ads RAG system.

## 🚀 **Quick Test Commands**

### **1. Query the RAG System**
```bash
curl -X POST 'http://localhost:8000/google-ads-new/api/rag/query/' \
  -H 'Content-Type: application/json' \
  -d '{"query": "How do I get started with Google Ads API?"}'
```

### **2. Search for Similar Documents**
```bash
curl -X POST 'http://localhost:8000/google-ads-new/api/rag/search/' \
  -H 'Content-Type: application/json' \
  -d '{"query": "OAuth setup", "limit": 5}'
```

### **3. Get System Status**
```bash
curl -X GET 'http://localhost:8000/google-ads-new/api/rag/status/'
```

### **4. Rebuild Vector Store**
```bash
curl -X POST 'http://localhost:8000/google-ads-new/api/rag/rebuild/'
```

## 🔐 **Authenticated Endpoints (Require JWT Token)**

### **5. Authenticated Query**
```bash
curl -X POST 'http://localhost:8000/google-ads-new/api/rag/api/query/' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer <your_jwt_token>' \
  -d '{"query": "How do I create a campaign?"}'
```

### **6. Authenticated Document Search**
```bash
curl -X POST 'http://localhost:8000/google-ads-new/api/rag/api/search/' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer <your_jwt_token>' \
  -d '{"query": "account management", "limit": 3}'
```

### **7. Authenticated Status Check**
```bash
curl -X GET 'http://localhost:8000/google-ads-new/api/rag/api/status/' \
  -H 'Authorization: Bearer <your_jwt_token>'
```

## 🧪 **Test Queries for Different Topics**

### **Getting Started**
```bash
curl -X POST 'http://localhost:8000/google-ads-new/api/rag/query/' \
  -H 'Content-Type: application/json' \
  -d '{"query": "What is the Google Ads API and how do I get started?"}'
```

### **Authentication & OAuth**
```bash
curl -X POST 'http://localhost:8000/google-ads-new/api/rag/query/' \
  -H 'Content-Type: application/json' \
  -d '{"query": "How do I set up OAuth for Google Ads API?"}'
```

### **Campaign Management**
```bash
curl -X POST 'http://localhost:8000/google-ads-new/api/rag/query/' \
  -H 'Content-Type: application/json' \
  -d '{"query": "How do I create and manage campaigns using the API?"}'
```

### **Account Management**
```bash
curl -X POST 'http://localhost:8000/google-ads-new/api/rag/query/' \
  -H 'Content-Type: application/json' \
  -d '{"query": "How do I manage Google Ads accounts and users?"}'
```

### **Common Errors**
```bash
curl -X POST 'http://localhost:8000/google-ads-new/api/rag/query/' \
  -H 'Content-Type: application/json' \
  -d '{"query": "What are the common errors in Google Ads API and how to fix them?"}'
```

### **API Concepts**
```bash
curl -X POST 'http://localhost:8000/google-ads-new/api/rag/query/' \
  -H 'Content-Type: application/json' \
  -d '{"query": "Explain the Google Ads API structure and concepts"}'
```

### **Mutating Data**
```bash
curl -X POST 'http://localhost:8000/google-ads-new/api/rag/query/' \
  -H 'Content-Type: application/json' \
  -d '{"query": "How do I create, update, and delete objects in Google Ads API?"}'
```

## 🔍 **Document Search Examples**

### **Search by Topic**
```bash
curl -X POST 'http://localhost:8000/google-ads-new/api/rag/search/' \
  -H 'Content-Type: application/json' \
  -d '{"query": "developer token", "limit": 3}'
```

### **Search by Feature**
```bash
curl -X POST 'http://localhost:8000/google-ads-new/api/rag/search/' \
  -H 'Content-Type: application/json' \
  -d '{"query": "bulk operations", "limit": 5}'
```

### **Search by Error Type**
```bash
curl -X POST 'http://localhost:8000/google-ads-new/api/rag/search/' \
  -H 'Content-Type: application/json' \
  -d '{"query": "authentication errors", "limit": 4}'
```

## 📊 **System Monitoring**

### **Check Collection Stats**
```bash
curl -X GET 'http://localhost:8000/google-ads-new/api/rag/status/' | jq '.collection_stats'
```

### **Test System Health**
```bash
curl -X GET 'http://localhost:8000/google-ads-new/api/rag/status/' | jq '.success'
```

## 🚨 **Error Testing**

### **Invalid Query**
```bash
curl -X POST 'http://localhost:8000/google-ads-new/api/rag/query/' \
  -H 'Content-Type: application/json' \
  -d '{"query": ""}'
```

### **Invalid JSON**
```bash
curl -X POST 'http://localhost:8000/google-ads-new/api/rag/query/' \
  -H 'Content-Type: application/json' \
  -d '{"query": "test"'
```

### **Missing Content-Type**
```bash
curl -X POST 'http://localhost:8000/google-ads-new/api/rag/query/' \
  -d '{"query": "test"}'
```

## 🔄 **Batch Testing Script**

Create a file `test_rag_curl.sh`:

```bash
#!/bin/bash

BASE_URL="http://localhost:8000/google-ads-new/api/rag"

echo "Testing RAG System with cURL"
echo "=============================="

# Test 1: Basic query
echo "1. Testing basic query..."
curl -X POST "$BASE_URL/query/" \
  -H 'Content-Type: application/json' \
  -d '{"query": "How do I get started with Google Ads API?"}' \
  | jq '.success, .answer[:100]'

echo -e "\n"

# Test 2: Document search
echo "2. Testing document search..."
curl -X POST "$BASE_URL/search/" \
  -H 'Content-Type: application/json' \
  -d '{"query": "OAuth", "limit": 3}' \
  | jq '.success, .count'

echo -e "\n"

# Test 3: Status check
echo "3. Testing status check..."
curl -X GET "$BASE_URL/status/" \
  | jq '.success, .collection_stats'

echo -e "\n"

# Test 4: Multiple queries
echo "4. Testing multiple queries..."
queries=(
  "What is OAuth?"
  "How do I create a campaign?"
  "What are common API errors?"
  "How do I manage accounts?"
)

for query in "${queries[@]}"; do
  echo "Query: $query"
  curl -X POST "$BASE_URL/query/" \
    -H 'Content-Type: application/json' \
    -d "{\"query\": \"$query\"}" \
    | jq '.success, .answer[:50]'
  echo -e "\n"
done
```

Make it executable and run:
```bash
chmod +x test_rag_curl.sh
./test_rag_curl.sh
```

## 📝 **Expected Responses**

### **Successful Query Response**
```json
{
  "success": true,
  "answer": "To get started with Google Ads API, you need to...",
  "sources": [
    {
      "source": "https://developers.google.com/google-ads/api/docs/get-started/introduction",
      "chunk": 0,
      "section": "getting_started",
      "text_preview": "The Google Ads API allows you to..."
    }
  ],
  "query": "How do I get started with Google Ads API?"
}
```

### **Document Search Response**
```json
{
  "success": true,
  "query": "OAuth setup",
  "documents": [
    {
      "source": "https://developers.google.com/google-ads/api/docs/oauth/overview",
      "chunk": 0,
      "section": "oauth",
      "text": "OAuth 2.0 is the authentication protocol...",
      "metadata": {...}
    }
  ],
  "count": 3
}
```

### **Status Response**
```json
{
  "success": true,
  "status": "active",
  "collection_stats": {
    "collection_name": "google_ads_docs",
    "total_points": 1250,
    "indexed_vectors": 1250,
    "vectors_count": 1250
  }
}
```

## 🛠️ **Troubleshooting**

### **Connection Refused**
```bash
# Check if Django server is running
curl -X GET 'http://localhost:8000/google-ads-new/api/rag/status/'
```

### **404 Not Found**
```bash
# Check if URLs are correct
curl -X GET 'http://localhost:8000/google-ads-new/api/rag/status/'
```

### **500 Internal Server Error**
```bash
# Check Django logs
python manage.py runserver --verbosity=2
```

### **Empty Response**
```bash
# Check if RAG system is set up
python manage.py setup_rag
```

## 🎯 **Performance Testing**

### **Load Testing with Apache Bench**
```bash
# Test query endpoint
ab -n 100 -c 10 -p query.json -T 'application/json' \
  'http://localhost:8000/google-ads-new/api/rag/query/'

# Create query.json file
echo '{"query": "How do I create a campaign?"}' > query.json
```

### **Response Time Testing**
```bash
# Time a single query
time curl -X POST 'http://localhost:8000/google-ads-new/api/rag/query/' \
  -H 'Content-Type: application/json' \
  -d '{"query": "How do I get started with Google Ads API?"}'
```

## 📋 **Quick Reference**

| Endpoint | Method | Auth Required | Purpose |
|----------|--------|---------------|---------|
| `/api/rag/query/` | POST | No | Query the RAG system |
| `/api/rag/search/` | POST | No | Search documents |
| `/api/rag/status/` | GET | No | Get system status |
| `/api/rag/rebuild/` | POST | No | Rebuild vector store |
| `/api/rag/api/query/` | POST | Yes | Authenticated query |
| `/api/rag/api/search/` | POST | Yes | Authenticated search |
| `/api/rag/api/status/` | GET | Yes | Authenticated status |

## 🚀 **Next Steps**

1. **Set up the system**: `python manage.py setup_rag`
2. **Test basic functionality**: Use the quick test commands above
3. **Run comprehensive tests**: Use the batch testing script
4. **Monitor performance**: Use the performance testing commands
5. **Integrate with your application**: Use the Python integration examples

Happy testing! 🎉

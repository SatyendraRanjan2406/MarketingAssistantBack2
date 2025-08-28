# 📚 Knowledge Base Setup and Usage Guide

## Overview

This guide explains how to add, manage, and use knowledge base documents in your Google Ads chatbot system. The knowledge base provides comprehensive information about Google Ads, enabling the chatbot to give accurate, detailed answers to user queries.

## 🚀 Quick Start

### 1. **Add the Google Search Ads Knowledge Base**

Run the setup script to add the comprehensive knowledge base:

```bash
python add_knowledge_base.py
```

This will:
- Create/update the Google Search Ads knowledge base document
- Test the knowledge base search functionality
- Verify integration with the chatbot system

### 2. **Verify the Setup**

Check that the knowledge base was added successfully:

```bash
# Check Django admin interface
# Or use the Django shell
python manage.py shell
```

```python
from google_ads_new.models import KBDocument
doc = KBDocument.objects.filter(title__icontains="Google Search Ads").first()
print(f"Document: {doc.title}")
print(f"Content length: {len(doc.content)} characters")
```

## 📋 Step-by-Step Setup Process

### **Step 1: Prepare Your Knowledge Base Document**

1. **Create a Markdown file** with your knowledge base content
2. **Use proper structure** with headers, lists, and formatting
3. **Include metadata** like tags, categories, and version information
4. **Save in the knowledge_base/ directory**

Example structure:
```markdown
# Document Title

## Section 1
Content here...

## Section 2
Content here...

---
**Tags**: tag1, tag2, tag3
**Category**: Main Category
**Version**: 1.0.0
```

### **Step 2: Create the Setup Script**

Use the provided `add_knowledge_base.py` script as a template:

```python
def add_knowledge_base():
    # Read your knowledge base file
    with open("path/to/your/kb_file.md", 'r') as file:
        content = file.read()
    
    # Create the document
    kb_doc = KBDocument.objects.create(
        company_id=1,
        title="Your Knowledge Base Title",
        content=content,
        document_type="knowledge_base",
        metadata={
            "category": "Your Category",
            "tags": ["tag1", "tag2"],
            "version": "1.0.0"
        }
    )
```

### **Step 3: Run the Setup**

```bash
python add_knowledge_base.py
```

### **Step 4: Test the Integration**

The setup script automatically tests:
- Document creation/update
- Search functionality
- Integration with the chatbot system

## 🔧 Knowledge Base Management

### **Adding New Documents**

```python
from google_ads_new.models import KBDocument

# Create a new knowledge base document
kb_doc = KBDocument.objects.create(
    company_id=1,
    title="New Knowledge Base Title",
    content="Your content here...",
    document_type="knowledge_base",
    url="",
    metadata={
        "category": "Category",
        "subcategory": "Subcategory",
        "tags": ["tag1", "tag2"],
        "version": "1.0.0",
        "author": "Author Name",
        "difficulty_level": "Beginner/Intermediate/Advanced",
        "estimated_read_time": "15 minutes"
    }
)
```

### **Updating Existing Documents**

```python
# Find and update existing document
doc = KBDocument.objects.get(title="Document Title")
doc.content = "Updated content..."
doc.metadata["version"] = "1.1.0"
doc.save()
```

### **Deleting Documents**

```python
# Delete a document
doc = KBDocument.objects.get(title="Document Title")
doc.delete()
```

### **Searching Documents**

```python
from google_ads_new.langchain_tools import KnowledgeBaseTools

kb_tools = KnowledgeBaseTools(user, session_id)
search_results = kb_tools.search_kb("your search query", company_id=1)
```

## 📊 Knowledge Base Structure

### **Document Types**

- **knowledge_base**: General knowledge and best practices
- **tutorial**: Step-by-step guides
- **reference**: Quick reference materials
- **case_study**: Real-world examples
- **faq**: Frequently asked questions

### **Metadata Fields**

```json
{
    "category": "Main category (e.g., Google Ads)",
    "subcategory": "Subcategory (e.g., Search Ads)",
    "tags": ["tag1", "tag2", "tag3"],
    "version": "Document version",
    "author": "Author name",
    "difficulty_level": "Beginner/Intermediate/Advanced",
    "estimated_read_time": "Reading time estimate",
    "last_updated": "Last update date",
    "review_status": "Draft/Reviewed/Published"
}
```

### **Content Organization**

1. **Clear Headers**: Use proper markdown headers (# ## ###)
2. **Structured Lists**: Use bullet points and numbered lists
3. **Code Examples**: Include practical examples and formulas
4. **Cross-references**: Link related concepts within the document
5. **Actionable Content**: Provide specific recommendations and steps

## 🔍 Using the Knowledge Base in Chatbot

### **Automatic Integration**

The chatbot automatically:
- Searches the knowledge base for relevant information
- Incorporates knowledge base content into responses
- Provides accurate, up-to-date information
- Suggests related topics and resources

### **Query Examples**

Users can ask questions like:
- "How do I calculate CTR?"
- "What are the different keyword match types?"
- "How can I optimize my Google Ads campaign?"
- "What factors affect Quality Score?"

### **Response Enhancement**

The knowledge base enhances chatbot responses by:
- Providing detailed explanations
- Including formulas and calculations
- Offering step-by-step guidance
- Suggesting best practices
- Referencing official documentation

## 🧪 Testing Your Knowledge Base

### **Test Search Functionality**

```python
# Test basic search
results = kb_tools.search_kb("CTR calculation", company_id=1)
print(f"Found {len(results['results'])} results")

# Test complex queries
results = kb_tools.search_kb("How to optimize Google Ads for better performance?", company_id=1)
```

### **Test Chatbot Integration**

1. **Start a chat session**
2. **Ask questions related to your knowledge base**
3. **Verify responses include knowledge base content**
4. **Check for accuracy and relevance**

### **Performance Testing**

```python
import time

start_time = time.time()
results = kb_tools.search_kb("test query", company_id=1)
end_time = time.time()

print(f"Search completed in {end_time - start_time:.2f} seconds")
```

## 📈 Best Practices

### **Content Quality**

1. **Accuracy**: Ensure all information is current and accurate
2. **Completeness**: Cover topics comprehensively
3. **Clarity**: Use clear, concise language
4. **Examples**: Include practical examples and use cases
5. **Updates**: Keep content current with platform changes

### **Organization**

1. **Logical Structure**: Organize content logically
2. **Consistent Formatting**: Use consistent markdown formatting
3. **Cross-references**: Link related concepts
4. **Tags**: Use relevant tags for better searchability
5. **Categories**: Group related content appropriately

### **Maintenance**

1. **Regular Reviews**: Review content monthly
2. **Version Control**: Track document versions
3. **User Feedback**: Incorporate user feedback
4. **Platform Updates**: Update content when platforms change
5. **Performance Monitoring**: Monitor search performance

## 🚨 Troubleshooting

### **Common Issues**

#### **Document Not Found**
```python
# Check if document exists
doc = KBDocument.objects.filter(title__icontains="Your Title").first()
if not doc:
    print("Document not found - create it first")
```

#### **Search Not Working**
```python
# Check knowledge base tools initialization
try:
    kb_tools = KnowledgeBaseTools(user, session_id)
    results = kb_tools.search_kb("test", company_id=1)
except Exception as e:
    print(f"Error: {e}")
```

#### **Poor Search Results**
```python
# Check document content and metadata
doc = KBDocument.objects.get(id=doc_id)
print(f"Content length: {len(doc.content)}")
print(f"Tags: {doc.metadata.get('tags', [])}")
```

### **Debug Commands**

```python
# List all knowledge base documents
docs = KBDocument.objects.all()
for doc in docs:
    print(f"ID: {doc.id}, Title: {doc.title}, Type: {doc.document_type}")

# Check document metadata
doc = KBDocument.objects.get(id=1)
print(f"Metadata: {doc.metadata}")

# Test search with specific document
results = kb_tools.search_kb("test query", company_id=1)
print(f"Search results: {results}")
```

## 🔮 Advanced Features

### **Custom Search Algorithms**

```python
# Implement custom search logic
def custom_search(query, company_id):
    # Your custom search implementation
    pass
```

### **Knowledge Base Analytics**

```python
# Track search performance
from django.db.models import Count
from google_ads_new.models import UserIntent

# Most common queries
common_queries = UserIntent.objects.values('user_query').annotate(
    count=Count('user_query')
).order_by('-count')[:10]
```

### **Automated Updates**

```python
# Schedule regular updates
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    def handle(self, *args, **options):
        # Your update logic here
        pass
```

## 📚 Example Knowledge Base Documents

### **Google Ads Performance Metrics**
- Core metrics (CTR, CPC, conversions)
- Calculation formulas
- Benchmark values
- Optimization strategies

### **Campaign Optimization**
- Bid management
- Budget allocation
- Keyword optimization
- Ad copy testing

### **Best Practices**
- Account structure
- Ad policies
- Quality Score factors
- Compliance guidelines

## 🎯 Next Steps

1. **Run the setup script** to add the Google Search Ads knowledge base
2. **Test the integration** with your chatbot
3. **Add more knowledge base documents** for other topics
4. **Customize the search functionality** for your specific needs
5. **Monitor performance** and gather user feedback
6. **Regularly update content** to keep it current

## 📞 Support

If you encounter issues:

1. **Check the troubleshooting section** above
2. **Review the Django logs** for error messages
3. **Verify database connections** and model setup
4. **Test with simple queries** first
5. **Check user permissions** and authentication

---

**Last Updated**: December 2024  
**Version**: 1.0.0  
**Maintainer**: Google Ads Development Team

# Packages to Uninstall

The following packages are no longer needed after commenting out RAGChatView, RAGChat2View, and RagChat3View:

## Unused Packages (can be uninstalled)

```bash
pip uninstall -y chromadb
pip uninstall -y langchain-chroma
pip uninstall -y sentence-transformers
pip uninstall -y pypdf
pip uninstall -y python-docx
pip uninstall -y beautifulsoup4
pip uninstall -y unstructured
```

## Packages Still Needed for LanggraphView

The following packages are still required for LanggraphView functionality:

- Django==5.2.5
- google-ads==28.0.0
- google-auth==2.40.3
- google-auth-oauthlib==1.2.2
- google-api-core==2.25.1
- requests==2.32.4
- python-dotenv==1.0.0
- protobuf>=5.0.0,<7.0.0
- djangorestframework==3.14.0
- django-cors-headers==4.3.1
- celery==5.3.4
- redis==5.0.1
- psycopg2-binary==2.9.9
- Pillow==10.1.0
- pandas>=2.3.0
- numpy>=2.3.0
- matplotlib>=3.8.0
- seaborn>=0.13.0
- langchain>=0.1.0
- langchain-openai>=0.0.5
- langchain-community>=0.0.10
- plotly>=6.0.0
- openai>=1.0.0
- tiktoken>=0.5.0
- langgraph>=0.6.0
- langgraph-checkpoint>=2.0.0
- langgraph-checkpoint-postgres>=2.0.0

## Summary

- **Commented out views**: RAGChatView, RAGChat2View, RagChat3View
- **Removed imports**: message_builder, google_ads_new.intent_mapping_service
- **Commented out URLs**: MCP Chat endpoint
- **Packages to uninstall**: 7 packages (chromadb, langchain-chroma, sentence-transformers, pypdf, python-docx, beautifulsoup4, unstructured)
- **LanggraphView status**: ✅ Working correctly after cleanup

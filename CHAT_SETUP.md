# Google Ads Chat Assistant Setup Guide

## Overview
This chat feature allows customers to interact with an AI assistant to analyze and process their Google Ads data. The assistant can provide text responses, generate charts, and suggest actions based on the data.

## Features
- 🤖 AI-powered chat interface
- 📊 Interactive charts and visualizations
- 💡 Automated insights and recommendations
- 🚀 Suggested actions for optimization
- 📈 Real-time data analysis

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Environment Variables
Create a `.env` file in your project root with the following variables:

```bash
# Google Ads API Configuration
GOOGLE_DEV_TOKEN=your_google_ads_developer_token
GOOGLE_ADS_CLIENT_ID=your_google_ads_client_id
GOOGLE_ADS_CLIENT_SECRET=your_google_ads_client_secret
GOOGLE_ADS_REFRESH_TOKEN=your_google_ads_refresh_token
GOOGLE_ADS_LOGIN_CUSTOMER_ID=your_google_ads_login_customer_id

# OpenAI API Configuration for Chat Assistant
OPENAI_API_KEY=your_openai_api_key

# Redis Configuration (optional, for Celery)
REDIS_URL=redis://localhost:6379/0
```

### 3. Get OpenAI API Key
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Create an account or sign in
3. Navigate to API Keys section
4. Create a new API key
5. Add it to your `.env` file

### 4. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Start the Development Server
```bash
python manage.py runserver
```

### 6. Access the Chat Interface
Navigate to: `http://localhost:8000/google-ads/chat/`

## Usage Examples

### Sample Questions Users Can Ask:
- "How are my campaigns performing this month?"
- "Which keywords have the best conversion rate?"
- "What can I do to improve my ROAS?"
- "Show me a breakdown of my ad spend by campaign"
- "Which campaigns are underperforming?"

### What the Assistant Provides:
1. **Text Responses**: Clear explanations and insights
2. **Charts**: Interactive visualizations (line, bar, pie, tables)
3. **Actions**: Specific recommendations for improvement
4. **Data Summary**: Key metrics and findings

## Architecture

### Components:
- **Chat Service** (`chat_service.py`): Core AI logic using LangChain
- **Views** (`views.py`): Django views for chat interface
- **Templates** (`chat_dashboard.html`): Modern chat UI
- **URLs** (`urls.py`): Routing for chat endpoints

### Technology Stack:
- **Backend**: Django + Django REST Framework
- **AI Framework**: LangChain (easier than LangGraph for MVP)
- **LLM**: OpenAI GPT-3.5-turbo
- **Charts**: Plotly.js for interactive visualizations
- **Frontend**: Modern HTML/CSS/JavaScript

## Why LangChain over LangGraph?

For your MVP with budget constraints and single developer:

### LangChain Advantages:
✅ **Faster Development**: Get working in days, not weeks
✅ **Lower Learning Curve**: Simpler abstractions
✅ **Better Documentation**: More tutorials and examples
✅ **Cost-Effective**: Works with free/open-source options
✅ **Community Support**: Larger ecosystem

### LangGraph Advantages:
✅ **Complex Workflows**: Better for multi-step processes
✅ **State Management**: Advanced conversation state handling
✅ **Custom Logic**: More control over flow

## Cost Considerations

### OpenAI API Costs (GPT-3.5-turbo):
- **Input**: $0.0015 per 1K tokens
- **Output**: $0.002 per 1K tokens
- **Typical chat**: ~$0.01-0.05 per conversation
- **Monthly estimate**: $10-50 for moderate usage

### Alternatives for Budget Constraints:
1. **Open Source LLMs**: Use local models (slower but free)
2. **Hugging Face**: Free tier available
3. **Anthropic Claude**: Competitive pricing

## Customization

### Adding Meta Ads Support:
1. Install Meta Business SDK
2. Create MetaAdsService similar to GoogleAdsService
3. Extend chat service to handle Meta data
4. Update prompts to include Meta Ads knowledge

### Adding More Chart Types:
1. Extend `create_performance_chart` method
2. Add new chart types (scatter, heatmap, etc.)
3. Update frontend to handle new chart types

## Troubleshooting

### Common Issues:
1. **OpenAI API Key Error**: Check `.env` file and API key validity
2. **Chart Rendering Issues**: Ensure Plotly.js is loaded
3. **Data Loading Errors**: Verify Google Ads API credentials
4. **Memory Issues**: Consider using smaller LLM models

### Performance Tips:
1. Cache frequently requested data
2. Use async processing for long operations
3. Implement rate limiting for API calls
4. Optimize database queries

## Next Steps

### Phase 2 Enhancements:
- [ ] Meta Ads integration
- [ ] Advanced analytics
- [ ] Automated reporting
- [ ] Multi-language support
- [ ] Mobile app

### Phase 3 Features:
- [ ] Predictive analytics
- [ ] A/B testing suggestions
- [ ] Budget optimization
- [ ] Competitor analysis

## Support

For issues or questions:
1. Check Django logs for errors
2. Verify API credentials
3. Test with simple queries first
4. Check browser console for frontend issues

---

**Note**: This is an MVP implementation. For production use, consider adding authentication, rate limiting, error handling, and security measures.

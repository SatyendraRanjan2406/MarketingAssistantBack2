# Ad Expert - Privacy-First AI Chat Assistant

A senior platform engineer-designed chat system for Google Ads and Meta Marketing API analysis with privacy-first architecture, in-memory analytics, and user-controlled chat history.

## 🎯 Core Principles

- **Privacy-First**: No campaign data at rest - process in memory and discard after responding
- **User-Controlled**: Only chat history (natural language) is stored; users can purge anytime
- **Zero Training Risk**: Use OpenAI API where business data isn't used for training by default
- **On-Demand Data**: Pull live campaign data only when user explicitly asks

## 🏗️ Architecture

### High-Level Design
```
Client (Web/App) → Backend API → LLM Orchestrator → API Tools → Live Data Sources
                                    ↓
                              In-Memory Analytics
                                    ↓
                              Structured Response
```

### Data Flow (Per User Query)
1. User asks: "What's my CPA trend last 14 days for Search vs Reels?"
2. LLM decides which tool(s) to call:
   - `get_google_insights` (date range, segments)
   - `get_meta_insights` (breakdowns)
3. Backend tools perform live API calls, stream results into memory, compute aggregations
4. LLM drafts explanation + next-best actions
5. Response rendered, memory cleared, only chat message text stored

## 📊 Response Formats

The system supports multiple response formats for rich user experience:

- **Text**: Narrative explanations
- **Bullets**: Key takeaways and highlights
- **Tables**: KPI comparisons and data grids
- **Charts**: Line charts (trends), bar charts (comparisons), pie charts (distributions)
- **Action Items**: Optimization checklists
- **Links**: External resources and campaign links

### Example Response Structure
```json
{
  "response_type": "line_chart",
  "title": "CPA Trend (Last 14 Days)",
  "content": "Your CPA has been trending downward over the past 14 days...",
  "data": [
    {"label": "2025-08-20", "value": 32.5, "description": "Spend: $1,250"},
    {"label": "2025-08-21", "value": 31.2, "description": "Spend: $1,180"}
  ],
  "insights": [
    "CPA decreased by 8% week-over-week",
    "Search campaigns outperforming Reels by 15%"
  ]
}
```

## 🔧 API Endpoints

### Chat Endpoints
- `POST /ad-expert/api/chat/message/` - Send chat message
- `GET /ad-expert/api/conversations/` - Get user conversations
- `GET /ad-expert/api/conversations/{id}/` - Get conversation messages
- `DELETE /ad-expert/api/conversations/{id}/delete/` - Delete conversation

### OAuth Management
- `GET /ad-expert/api/oauth/connections/` - Get OAuth connections
- `DELETE /ad-expert/api/oauth/connections/{id}/revoke/` - Revoke connection

### Health Check
- `GET /ad-expert/api/health/` - System health status

## 🔐 Security & Privacy

### OAuth Implementation
- **Google Ads**: OAuth web flow with `https://www.googleapis.com/auth/adwords` scope
- **Meta Marketing**: App Review for `ads_read`/`ads_management` permissions
- **Token Management**: Short-lived access tokens, no refresh tokens persisted unless user opts-in
- **Encryption**: Access tokens encrypted in production (KMS/HSM)

### Data Protection
- **No Campaign Data Storage**: Raw campaign data never persisted
- **In-Memory Processing**: All analytics computed in memory and discarded
- **Chat History Only**: Only natural language messages stored
- **User Control**: Users can purge chat history anytime
- **PII Filtering**: Never send emails/phone/creative text to LLM unless requested

### Observability
- **Metrics Only**: Log latency, counts, error codes (no content)
- **Rate Limiting**: Exponential backoff + circuit breaker for API calls
- **Audit Trail**: Track OAuth connections and chat sessions

## 🛠️ Technical Implementation

### Models
```python
# Only stores natural language chat data
class Conversation(models.Model):
    user = models.ForeignKey(User)
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField()
    deleted_at = models.DateTimeField(null=True)  # Soft delete

class ChatMessage(models.Model):
    conversation = models.ForeignKey(Conversation)
    role = models.CharField(choices=['user', 'assistant', 'system'])
    content = models.TextField()
    response_type = models.CharField()  # text, chart, table, etc.
    structured_data = models.JSONField()  # For charts, tables

class OAuthConnection(models.Model):
    user = models.ForeignKey(User)
    platform = models.CharField(choices=['google', 'meta'])
    access_token = models.TextField()  # Encrypted
    token_expires_at = models.DateTimeField()
    account_id = models.CharField()
```

### API Tools
- **GoogleAdsAPITool**: Fetches Google Ads data via GAQL, processes KPIs in memory
- **MetaMarketingAPITool**: Fetches Meta Insights data, computes trends and metrics
- **In-Memory Analytics**: Computes CTR, CPC, CPA, trends, anomalies without storage

### LLM Orchestrator
- **OpenAI Responses API**: Uses latest API with tool calling
- **Structured Outputs**: JSON schema for multiple response formats
- **Tool Calling**: Automatic decision on which data sources to query
- **Context Management**: Maintains conversation context without storing campaign data

## 🚀 Setup & Configuration

### Environment Variables
```bash
# OpenAI
OPENAI_API_KEY=your_openai_api_key

# Google OAuth
GOOGLE_OAUTH_CLIENT_ID=your_google_client_id
GOOGLE_OAUTH_CLIENT_SECRET=your_google_client_secret
GOOGLE_OAUTH_REDIRECT_URI=http://localhost:8000/ad-expert/api/oauth/google/callback/

# Google Ads
GOOGLE_ADS_DEVELOPER_TOKEN=your_developer_token

# Meta OAuth
META_APP_ID=your_meta_app_id
META_APP_SECRET=your_meta_app_secret
META_REDIRECT_URI=http://localhost:8000/ad-expert/api/oauth/meta/callback/
```

### Database Migration
```bash
python manage.py makemigrations ad_expert
python manage.py migrate ad_expert
```

### Admin Interface
Access Django admin to manage:
- Conversations and chat messages
- OAuth connections
- User permissions

## 📈 Usage Examples

### Basic Chat
```bash
curl -X POST http://localhost:8000/ad-expert/api/chat/message/ \
  -H "Authorization: Bearer your_jwt_token" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is my CPA trend for the last 14 days?"}'
```

### Get Conversations
```bash
curl -X GET http://localhost:8000/ad-expert/api/conversations/ \
  -H "Authorization: Bearer your_jwt_token"
```

### Delete Conversation
```bash
curl -X DELETE http://localhost:8000/ad-expert/api/conversations/123/delete/ \
  -H "Authorization: Bearer your_jwt_token"
```

## 🔄 Data Flow Example

1. **User Query**: "Show me my top performing campaigns this week"
2. **LLM Decision**: Calls `get_google_insights` and `get_meta_insights`
3. **API Calls**: Live data fetched from Google Ads and Meta APIs
4. **In-Memory Analysis**: KPIs computed, campaigns ranked, trends identified
5. **Structured Response**: Returns bar chart with top campaigns and action items
6. **Storage**: Only chat message text saved, campaign data discarded
7. **User Experience**: Rich visualization with actionable insights

## 🛡️ Compliance & Best Practices

### GDPR/CCPA Compliance
- **Data Minimization**: Only store necessary chat history
- **User Rights**: Easy data deletion and export
- **Consent**: Clear opt-in for OAuth connections
- **Transparency**: Document data flow and retention policies

### API Rate Limiting
- **Google Ads**: Respect quota limits with exponential backoff
- **Meta Marketing**: Handle rate limits gracefully
- **Circuit Breaker**: Prevent cascade failures

### Monitoring & Alerting
- **Health Checks**: Regular system health monitoring
- **Error Tracking**: Comprehensive error logging
- **Performance Metrics**: Response time and throughput monitoring
- **Security Alerts**: Unusual access pattern detection

## 🔮 Future Enhancements

- **Streaming Responses**: Real-time chat with streaming updates
- **Advanced Analytics**: Machine learning insights and predictions
- **Multi-Language Support**: International campaign analysis
- **Custom Dashboards**: User-defined analytics views
- **API Webhooks**: Real-time campaign alerts and notifications

## 📚 Documentation References

- [Google Ads API Documentation](https://developers.google.com/google-ads/api)
- [Meta Marketing API Documentation](https://developers.facebook.com/docs/marketing-api)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Django REST Framework](https://www.django-rest-framework.org/)

---

**Built with privacy-first principles for enterprise-grade advertising analytics.**


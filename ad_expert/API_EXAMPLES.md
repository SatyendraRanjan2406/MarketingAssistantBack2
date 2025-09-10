# Ad Expert API Examples - Chat Message Endpoint

## Endpoint: `POST /ad-expert/api/chat/message/`

### Authentication
All requests require JWT authentication. Include the Bearer token in the Authorization header.

---

## Example 1: Basic Text Query

### Request
```bash
curl -X POST http://localhost:8000/ad-expert/api/chat/message/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, can you help me analyze my Google Ads performance?"
  }'
```

### Response
```json
{
  "message_id": 1,
  "conversation_id": 1,
  "response": {
    "response_type": "text",
    "title": "Welcome to Ad Expert",
    "content": "Hello! I'm your AI advertising co-pilot. I can help you analyze your Google Ads and Meta Marketing campaigns. To get started, I'll need you to connect your accounts first.\n\nI can help you with:\n• Campaign performance analysis\n• CPA and ROI trends\n• Budget optimization recommendations\n• Cross-platform comparisons\n• Actionable insights and next steps\n\nWould you like to connect your Google Ads or Meta account to begin?",
    "data": [],
    "insights": [
      "Connect your Google Ads account for search campaign analysis",
      "Connect your Meta account for social media campaign insights"
    ]
  },
  "timestamp": "2025-01-27T10:30:00.123456Z"
}
```

---

## Example 2: Google Ads Performance Query (with connected account)

### Request
```bash
curl -X POST http://localhost:8000/ad-expert/api/chat/message/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is my CPA trend for the last 14 days?",
    "conversation_id": 1
  }'
```

### Response
```json
{
  "message_id": 2,
  "conversation_id": 1,
  "response": {
    "response_type": "line_chart",
    "title": "CPA Trend - Last 14 Days",
    "content": "Your CPA has been trending downward over the past 14 days, showing a 12% improvement. Here's the detailed breakdown:",
    "data": [
      {
        "label": "2025-01-14",
        "value": 45.20,
        "description": "CPA: $45.20, Spend: $2,250"
      },
      {
        "label": "2025-01-15",
        "value": 43.80,
        "description": "CPA: $43.80, Spend: $2,190"
      },
      {
        "label": "2025-01-16",
        "value": 42.15,
        "description": "CPA: $42.15, Spend: $2,108"
      },
      {
        "label": "2025-01-17",
        "value": 41.90,
        "description": "CPA: $41.90, Spend: $2,095"
      },
      {
        "label": "2025-01-18",
        "value": 40.25,
        "description": "CPA: $40.25, Spend: $2,013"
      },
      {
        "label": "2025-01-19",
        "value": 39.80,
        "description": "CPA: $39.80, Spend: $1,990"
      },
      {
        "label": "2025-01-20",
        "value": 38.45,
        "description": "CPA: $38.45, Spend: $1,923"
      },
      {
        "label": "2025-01-21",
        "value": 37.20,
        "description": "CPA: $37.20, Spend: $1,860"
      },
      {
        "label": "2025-01-22",
        "value": 36.80,
        "description": "CPA: $36.80, Spend: $1,840"
      },
      {
        "label": "2025-01-23",
        "value": 35.90,
        "description": "CPA: $35.90, Spend: $1,795"
      },
      {
        "label": "2025-01-24",
        "value": 35.15,
        "description": "CPA: $35.15, Spend: $1,758"
      },
      {
        "label": "2025-01-25",
        "value": 34.80,
        "description": "CPA: $34.80, Spend: $1,740"
      },
      {
        "label": "2025-01-26",
        "value": 33.95,
        "description": "CPA: $33.95, Spend: $1,698"
      },
      {
        "label": "2025-01-27",
        "value": 32.50,
        "description": "CPA: $32.50, Spend: $1,625"
      }
    ],
    "insights": [
      "CPA decreased by 12% over 14 days",
      "Best performing day: Jan 27 with $32.50 CPA",
      "Consistent downward trend indicates optimization success",
      "Consider increasing budget on high-performing days"
    ]
  },
  "timestamp": "2025-01-27T10:35:00.123456Z"
}
```

---

## Example 3: Campaign Comparison Table

### Request
```bash
curl -X POST http://localhost:8000/ad-expert/api/chat/message/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show me a comparison of my top 5 campaigns by spend",
    "conversation_id": 1
  }'
```

### Response
```json
{
  "message_id": 3,
  "conversation_id": 1,
  "response": {
    "response_type": "table",
    "title": "Top 5 Campaigns by Spend",
    "content": "Here's a detailed comparison of your top 5 campaigns ranked by spend:",
    "data": [
      {
        "label": "Campaign Name",
        "value": "Performance Metrics",
        "description": "Search - Brand Keywords"
      },
      {
        "label": "Spend",
        "value": 12500.00,
        "description": "$12,500"
      },
      {
        "label": "Impressions",
        "value": 45000,
        "description": "45,000"
      },
      {
        "label": "Clicks",
        "value": 1800,
        "description": "1,800"
      },
      {
        "label": "CTR",
        "value": 4.0,
        "description": "4.0%"
      },
      {
        "label": "CPC",
        "value": 6.94,
        "description": "$6.94"
      },
      {
        "label": "Conversions",
        "value": 45,
        "description": "45"
      },
      {
        "label": "CPA",
        "value": 277.78,
        "description": "$277.78"
      }
    ],
    "insights": [
      "Brand Keywords campaign has highest spend but good CTR",
      "CPA is above average - consider optimizing landing pages",
      "Strong impression volume indicates good reach"
    ]
  },
  "timestamp": "2025-01-27T10:40:00.123456Z"
}
```

---

## Example 4: Action Items Response

### Request
```bash
curl -X POST http://localhost:8000/ad-expert/api/chat/message/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What optimizations should I make to improve my campaign performance?",
    "conversation_id": 1
  }'
```

### Response
```json
{
  "message_id": 4,
  "conversation_id": 1,
  "response": {
    "response_type": "action_items",
    "title": "Campaign Optimization Recommendations",
    "content": "Based on your recent performance data, here are the key optimizations I recommend:",
    "data": [
      {
        "label": "Pause underperforming keywords with CPA > $50",
        "value": 0,
        "description": "Priority: High - Expected savings: $2,000/month"
      },
      {
        "label": "Increase budget by 20% on top-performing campaigns",
        "value": 0,
        "description": "Priority: High - Expected ROI improvement: 15%"
      },
      {
        "label": "Test new ad copy for campaigns with CTR < 2%",
        "value": 0,
        "description": "Priority: Medium - Expected CTR improvement: 0.5%"
      },
      {
        "label": "Optimize landing pages for campaigns with high bounce rate",
        "value": 0,
        "description": "Priority: Medium - Expected conversion improvement: 10%"
      },
      {
        "label": "Implement negative keyword lists for broad match campaigns",
        "value": 0,
        "description": "Priority: Low - Expected CPC reduction: 5%"
      },
      {
        "label": "Set up automated bidding for campaigns with consistent performance",
        "value": 0,
        "description": "Priority: Low - Expected efficiency gain: 8%"
      }
    ],
    "insights": [
      "Focus on high-priority items first for maximum impact",
      "Monitor performance for 7 days after implementing changes",
      "Consider A/B testing before full rollout"
    ]
  },
  "timestamp": "2025-01-27T10:45:00.123456Z"
}
```

---

## Example 5: Bar Chart Response

### Request
```bash
curl -X POST http://localhost:8000/ad-expert/api/chat/message/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Compare my campaign performance by device type",
    "conversation_id": 1
  }'
```

### Response
```json
{
  "message_id": 5,
  "conversation_id": 1,
  "response": {
    "response_type": "bar_chart",
    "title": "Campaign Performance by Device Type",
    "content": "Here's how your campaigns perform across different device types:",
    "data": [
      {
        "label": "Mobile",
        "value": 45.2,
        "description": "CPA: $45.20, CTR: 3.2%"
      },
      {
        "label": "Desktop",
        "value": 38.7,
        "description": "CPA: $38.70, CTR: 4.1%"
      },
      {
        "label": "Tablet",
        "value": 42.1,
        "description": "CPA: $42.10, CTR: 3.8%"
      }
    ],
    "insights": [
      "Desktop campaigns have lowest CPA and highest CTR",
      "Mobile campaigns need optimization - consider mobile-specific ad copy",
      "Tablet performance is moderate - test device-specific bidding"
    ]
  },
  "timestamp": "2025-01-27T10:50:00.123456Z"
}
```

---

## Example 6: Error Response (No OAuth Connection)

### Request
```bash
curl -X POST http://localhost:8000/ad-expert/api/chat/message/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show me my Google Ads performance",
    "conversation_id": 1
  }'
```

### Response (when no Google OAuth connection exists)
```json
{
  "message_id": 6,
  "conversation_id": 1,
  "response": {
    "response_type": "text",
    "title": "Account Connection Required",
    "content": "I'd love to help you analyze your Google Ads performance! However, I need you to connect your Google Ads account first.\n\nTo get started:\n1. Go to your account settings\n2. Click 'Connect Google Ads'\n3. Authorize access to your Google Ads data\n4. Select the account you want to analyze\n\nOnce connected, I can provide detailed insights about your campaigns, keywords, and performance metrics.",
    "data": [],
    "insights": [
      "Connect your Google Ads account to unlock performance analytics",
      "I can analyze campaigns, keywords, and conversion data",
      "All data is processed securely and never stored"
    ]
  },
  "timestamp": "2025-01-27T10:55:00.123456Z"
}
```

---

## Example 7: Cross-Platform Comparison

### Request
```bash
curl -X POST http://localhost:8000/ad-expert/api/chat/message/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Compare my Google Ads vs Meta performance for the last 7 days",
    "conversation_id": 1
  }'
```

### Response
```json
{
  "message_id": 7,
  "conversation_id": 1,
  "response": {
    "response_type": "comparison_table",
    "title": "Google Ads vs Meta Performance (Last 7 Days)",
    "content": "Here's a side-by-side comparison of your Google Ads and Meta Marketing performance:",
    "data": [
      {
        "label": "Platform",
        "value": "Google Ads",
        "description": "Meta Marketing"
      },
      {
        "label": "Spend",
        "value": 8500.00,
        "description": "$6,200.00"
      },
      {
        "label": "Impressions",
        "value": 125000,
        "description": "89,000"
      },
      {
        "label": "Clicks",
        "value": 3200,
        "description": "2,100"
      },
      {
        "label": "CTR",
        "value": 2.56,
        "description": "2.36%"
      },
      {
        "label": "CPC",
        "value": 2.66,
        "description": "$2.95"
      },
      {
        "label": "Conversions",
        "value": 85,
        "description": "62"
      },
      {
        "label": "CPA",
        "value": 100.00,
        "description": "$100.00"
      },
      {
        "label": "ROAS",
        "value": 4.2,
        "description": "3.8"
      }
    ],
    "insights": [
      "Google Ads has higher spend but better ROAS",
      "Meta campaigns have slightly higher CPC but similar CPA",
      "Both platforms show strong conversion performance",
      "Consider reallocating budget based on ROAS performance"
    ]
  },
  "timestamp": "2025-01-27T11:00:00.123456Z"
}
```

---

## Example 8: Links and Resources Response

### Request
```bash
curl -X POST http://localhost:8000/ad-expert/api/chat/message/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Give me links to my campaign dashboards and helpful resources",
    "conversation_id": 1
  }'
```

### Response
```json
{
  "message_id": 8,
  "conversation_id": 1,
  "response": {
    "response_type": "links",
    "title": "Campaign Resources & Dashboards",
    "content": "Here are quick links to your campaign dashboards and helpful resources:",
    "data": [
      {
        "label": "Google Ads Dashboard",
        "value": 0,
        "url": "https://ads.google.com/aw/campaigns?ocid=123456789",
        "description": "View your Google Ads campaigns and performance"
      },
      {
        "label": "Meta Ads Manager",
        "value": 0,
        "url": "https://business.facebook.com/adsmanager",
        "description": "Manage your Meta advertising campaigns"
      },
      {
        "label": "Google Ads Help Center",
        "value": 0,
        "url": "https://support.google.com/google-ads",
        "description": "Official Google Ads support and documentation"
      },
      {
        "label": "Meta Business Help",
        "value": 0,
        "url": "https://www.facebook.com/business/help",
        "description": "Meta Business support and best practices"
      },
      {
        "label": "Campaign Performance Report",
        "value": 0,
        "url": "https://ads.google.com/aw/reports",
        "description": "Download detailed performance reports"
      }
    ],
    "insights": [
      "Bookmark these links for quick access to your campaigns",
      "Use the help centers for detailed optimization guides",
      "Download reports for offline analysis"
    ]
  },
  "timestamp": "2025-01-27T11:05:00.123456Z"
}
```

---

## Error Responses

### 400 Bad Request - Missing Message
```json
{
  "error": "Message is required"
}
```

### 401 Unauthorized - Invalid Token
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error"
}
```

---

## Response Types Reference

| Type | Description | Use Case |
|------|-------------|----------|
| `text` | Plain text response | General questions, explanations |
| `bullets` | Bulleted list | Key points, summaries |
| `table` | Data table | KPI comparisons, metrics |
| `comparison_table` | Side-by-side comparison | Cross-platform analysis |
| `bar_chart` | Bar chart data | Performance comparisons |
| `pie_chart` | Pie chart data | Budget allocation, distribution |
| `line_chart` | Line chart data | Trends over time |
| `histogram` | Histogram data | Distribution analysis |
| `action_items` | Checklist format | Optimization recommendations |
| `links` | Clickable links | Resources, dashboards |

---

## Notes

- All timestamps are in ISO 8601 format
- JWT tokens should be included in the Authorization header
- The `conversation_id` is optional - if not provided, a new conversation is created
- Response data is structured for easy frontend rendering
- All campaign data is processed in memory and never stored
- Chat history is the only data persisted (and can be purged by users)


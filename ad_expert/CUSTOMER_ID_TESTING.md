# Ad Expert API Testing with Customer ID: 9762343117

## 🎯 **Your Google Ads Customer ID: 9762343117**

## 🔐 **Step 1: Authentication**

### **Login to get JWT token:**
```bash
curl -X POST http://localhost:8000/accounts/api/signin/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your_username",
    "password": "your_password"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Login successful!",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 2,
    "username": "your_username",
    "email": "user@example.com"
  },
  "google_account": {
    "connected": true,
    "email": "user@gmail.com"
  }
}
```

---

## 💬 **Step 2: Test Chat with Your Customer ID**

### **Basic Performance Query:**
```bash
curl -X POST http://localhost:8000/ad-expert/api/chat/message/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is my CPA trend for the last 14 days for customer ID 9762343117?"
  }'
```

### **Campaign Performance Analysis:**
```bash
curl -X POST http://localhost:8000/ad-expert/api/chat/message/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show me the performance of my top campaigns for customer 9762343117 in the last 7 days"
  }'
```

### **Budget Analysis:**
```bash
curl -X POST http://localhost:8000/ad-expert/api/chat/message/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Analyze my budget allocation and spending for customer ID 9762343117"
  }'
```

### **Keyword Performance:**
```bash
curl -X POST http://localhost:8000/ad-expert/api/chat/message/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are my best performing keywords for customer 9762343117?"
  }'
```

---

## 🔧 **Complete Working Example**

### **One-liner with your customer ID:**
```bash
# Get token and test chat in one command
TOKEN=$(curl -s -X POST http://localhost:8000/accounts/api/signin/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}' | \
  jq -r '.access_token') && \
curl -X POST http://localhost:8000/ad-expert/api/chat/message/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is my CPA trend for the last 14 days for customer ID 9762343117?"
  }'
```

---

## 📊 **Expected Response Types**

### **Line Chart Response (CPA Trend):**
```json
{
  "message_id": 1,
  "conversation_id": 1,
  "response": {
    "response_type": "line_chart",
    "title": "CPA Trend - Customer 9762343117 (Last 14 Days)",
    "content": "Your CPA has been trending downward over the past 14 days, showing a 12% improvement...",
    "data": [
      {
        "label": "2025-01-14",
        "value": 45.20,
        "description": "CPA: $45.20, Spend: $2,250"
      }
    ],
    "insights": [
      "CPA decreased by 12% over 14 days",
      "Best performing day: Jan 27 with $32.50 CPA"
    ]
  },
  "timestamp": "2025-01-27T12:00:00.123456Z"
}
```

### **Table Response (Campaign Comparison):**
```json
{
  "message_id": 2,
  "conversation_id": 1,
  "response": {
    "response_type": "table",
    "title": "Top Campaigns - Customer 9762343117",
    "content": "Here's a detailed comparison of your top campaigns...",
    "data": [
      {
        "label": "Campaign Name",
        "value": "Performance Metrics",
        "description": "Search - Brand Keywords"
      }
    ],
    "insights": [
      "Brand Keywords campaign has highest spend but good CTR"
    ]
  },
  "timestamp": "2025-01-27T12:05:00.123456Z"
}
```

---

## 🎯 **Specific Queries for Your Customer ID**

### **1. Performance Overview:**
```bash
curl -X POST http://localhost:8000/ad-expert/api/chat/message/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Give me a comprehensive performance overview for customer 9762343117"
  }'
```

### **2. Conversion Analysis:**
```bash
curl -X POST http://localhost:8000/ad-expert/api/chat/message/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Analyze my conversion rates and cost per conversion for customer 9762343117"
  }'
```

### **3. Device Performance:**
```bash
curl -X POST http://localhost:8000/ad-expert/api/chat/message/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How are my campaigns performing across different devices for customer 9762343117?"
  }'
```

### **4. Geographic Performance:**
```bash
curl -X POST http://localhost:8000/ad-expert/api/chat/message/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show me geographic performance breakdown for customer 9762343117"
  }'
```

### **5. Optimization Recommendations:**
```bash
curl -X POST http://localhost:8000/ad-expert/api/chat/message/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What optimizations do you recommend for customer 9762343117 based on current performance?"
  }'
```

---

## ⚠️ **Important Notes**

1. **Customer ID Format:** The system will automatically use your customer ID (9762343117) when you have Google OAuth connected
2. **OAuth Required:** Make sure your Google Ads account is connected via OAuth in the accounts app
3. **Token Expiry:** JWT tokens expire in 60 minutes, refresh as needed
4. **Data Privacy:** All campaign data is processed in memory and not stored
5. **Real-time Data:** Queries fetch live data from Google Ads API

---

## 🔍 **Troubleshooting**

### **If you get "Google Ads account not connected" error:**
1. Go to `/accounts/api/google-oauth/initiate/` to connect your Google Ads account
2. Ensure the connected account has access to customer ID 9762343117
3. Verify OAuth scopes include Google Ads access

### **If you get "No Google Ads customer ID found" error:**
1. Check that customer ID 9762343117 is properly set in your UserGoogleAuth record
2. Verify the account has proper permissions for this customer ID

---

## 🚀 **Ready to Test!**

Your customer ID (9762343117) is now ready to use with the ad_expert API. The system will automatically fetch live data from your Google Ads account and provide insights in various formats (charts, tables, action items, etc.).


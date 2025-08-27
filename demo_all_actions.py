#!/usr/bin/env python3
"""
Demo script to test all the new Google Ads analysis actions
This script demonstrates how to trigger each analysis action and see the responses
"""

import os
import django
import requests
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketing_assistant_project.settings')
django.setup()

def test_analysis_actions():
    """Test all the new analysis actions"""
    
    # Base URL for the API
    base_url = "http://localhost:8000/google-ads-new/api"
    
    # You'll need to get a valid JWT token from your frontend
    # For demo purposes, we'll show the expected API calls
    
    print("🚀 Google Ads Analysis Actions Demo")
    print("=" * 50)
    
    # List of all available analysis actions
    analysis_actions = [
        {
            "name": "Audience Analysis",
            "description": "Analyze audience size, overlap, and quality",
            "action": "ANALYZE_AUDIENCE",
            "message": "Analyze my audience size, overlap, and quality",
            "endpoint": f"{base_url}/chat/message/"
        },
        {
            "name": "Creative Fatigue Check",
            "description": "Monitor creative fatigue and variety",
            "action": "CHECK_CREATIVE_FATIGUE",
            "message": "Check for creative fatigue and variety in my campaigns",
            "endpoint": f"{base_url}/chat/message/"
        },
        {
            "name": "Video Performance Analysis",
            "description": "Analyze video completion rates and format performance",
            "action": "ANALYZE_VIDEO_PERFORMANCE",
            "message": "Analyze video completion rates and format performance",
            "endpoint": f"{base_url}/chat/message/"
        },
        {
            "name": "Performance Comparison",
            "description": "Compare performance across time periods",
            "action": "COMPARE_PERFORMANCE",
            "message": "Compare performance across time periods (M1 vs M2, MTD)",
            "endpoint": f"{base_url}/chat/message/"
        },
        {
            "name": "Campaign Optimization",
            "description": "Provide campaign-level optimization recommendations",
            "action": "OPTIMIZE_CAMPAIGN",
            "message": "Provide campaign optimization recommendations",
            "endpoint": f"{base_url}/chat/message/"
        },
        {
            "name": "Ad Set Optimization",
            "description": "Provide ad set-level optimization recommendations",
            "action": "OPTIMIZE_ADSET",
            "message": "Provide ad set optimization recommendations",
            "endpoint": f"{base_url}/chat/message/"
        },
        {
            "name": "Ad Optimization",
            "description": "Provide ad-level optimization recommendations",
            "action": "OPTIMIZE_AD",
            "message": "Provide ad-level optimization recommendations",
            "endpoint": f"{base_url}/chat/message/"
        },
        {
            "name": "Placement Analysis",
            "description": "Analyze placement performance (auto vs manual)",
            "action": "ANALYZE_PLACEMENTS",
            "message": "Analyze placement performance (auto vs manual)",
            "endpoint": f"{base_url}/chat/message/"
        },
        {
            "name": "Device Performance Analysis",
            "description": "Compare mobile vs desktop performance",
            "action": "ANALYZE_DEVICE_PERFORMANCE",
            "message": "Compare mobile vs desktop performance",
            "endpoint": f"{base_url}/chat/message/"
        },
        {
            "name": "Time Performance Analysis",
            "description": "Analyze day of week and hour performance",
            "action": "ANALYZE_TIME_PERFORMANCE",
            "message": "Analyze day of week and hour performance",
            "endpoint": f"{base_url}/chat/message/"
        },
        {
            "name": "Demographic Analysis",
            "description": "Analyze age and gender performance within segments",
            "action": "ANALYZE_DEMOGRAPHICS",
            "message": "Analyze age and gender performance within segments",
            "endpoint": f"{base_url}/chat/message/"
        },
        {
            "name": "Competitor Analysis",
            "description": "Monitor competitor creative activity and trends",
            "action": "ANALYZE_COMPETITORS",
            "message": "Monitor competitor creative activity and trends",
            "endpoint": f"{base_url}/chat/message/"
        },
        {
            "name": "Creative Element Testing",
            "description": "Test individual creative elements systematically",
            "action": "TEST_CREATIVE_ELEMENTS",
            "message": "Test individual creative elements systematically",
            "endpoint": f"{base_url}/chat/message/"
        },
        {
            "name": "Technical Compliance Check",
            "description": "Verify technical implementation and compliance",
            "action": "CHECK_TECHNICAL_COMPLIANCE",
            "message": "Verify pixel implementation, iOS attribution, and compliance",
            "endpoint": f"{base_url}/chat/message/"
        },
        {
            "name": "Audience Insights",
            "description": "Monitor audience saturation and cross-campaign attribution",
            "action": "ANALYZE_AUDIENCE_INSIGHTS",
            "message": "Monitor audience saturation and cross-campaign attribution",
            "endpoint": f"{base_url}/chat/message/"
        },
        {
            "name": "Budget Optimization",
            "description": "Provide budget optimization recommendations",
            "action": "OPTIMIZE_BUDGETS",
            "message": "Provide budget optimization recommendations",
            "endpoint": f"{base_url}/chat/message/"
        },
        {
            "name": "Campaign Consistency Check",
            "description": "Check keyword-ad consistency and ad group alignment",
            "action": "CHECK_CAMPAIGN_CONSISTENCY",
            "message": "Check keyword-ad consistency and ad group alignment",
            "endpoint": f"{base_url}/chat/message/"
        },
        {
            "name": "Sitelink Analysis",
            "description": "Verify 4-6 sitelinks are present and optimized",
            "action": "CHECK_SITELINKS",
            "message": "Check if 4-6 sitelinks are present and optimized",
            "endpoint": f"{base_url}/chat/message/"
        },
        {
            "name": "Landing Page URL Check",
            "description": "Validate LP URL functionality and keyword relevance",
            "action": "CHECK_LANDING_PAGE_URL",
            "message": "Validate landing page URL functionality and keyword relevance",
            "endpoint": f"{base_url}/chat/message/"
        },
        {
            "name": "Duplicate Keyword Check",
            "description": "Identify duplicate keywords across campaigns/ad groups",
            "action": "CHECK_DUPLICATE_KEYWORDS",
            "message": "Identify duplicate keywords across campaigns and ad groups",
            "endpoint": f"{base_url}/chat/message/"
        },
        {
            "name": "Keyword Trends Analysis",
            "description": "Monitor high-potential keywords with increasing search volume",
            "action": "ANALYZE_KEYWORD_TRENDS",
            "message": "Monitor high-potential keywords with increasing search volume",
            "endpoint": f"{base_url}/chat/message/"
        },
        {
            "name": "Auction Insights Analysis",
            "description": "Analyze competition and competitor ad strategies",
            "action": "ANALYZE_AUCTION_INSIGHTS",
            "message": "Analyze competition and competitor ad strategies",
            "endpoint": f"{base_url}/chat/message/"
        },
        {
            "name": "Search Term Analysis",
            "description": "Review search terms for negative keyword opportunities",
            "action": "ANALYZE_SEARCH_TERMS",
            "message": "Review search terms for negative keyword opportunities",
            "endpoint": f"{base_url}/chat/message/"
        },
        {
            "name": "Ads Showing Time Analysis",
            "description": "Analyze hour-of-day performance for bid optimization",
            "action": "ANALYZE_ADS_SHOWING_TIME",
            "message": "Analyze hour-of-day performance for bid optimization",
            "endpoint": f"{base_url}/chat/message/"
        },
        {
            "name": "Detailed Device Performance",
            "description": "Detailed device performance analysis for bid adjustments",
            "action": "ANALYZE_DEVICE_PERFORMANCE_DETAILED",
            "message": "Analyze device performance for bid adjustments",
            "endpoint": f"{base_url}/chat/message/"
        },
        {
            "name": "Location Performance Analysis",
            "description": "City-level performance analysis and optimization",
            "action": "ANALYZE_LOCATION_PERFORMANCE",
            "message": "Analyze city-level performance and optimization",
            "endpoint": f"{base_url}/chat/message/"
        },
        {
            "name": "Mobile Landing Page Analysis",
            "description": "Mobile speed score and optimization analysis",
            "action": "ANALYZE_LANDING_PAGE_MOBILE",
            "message": "Check mobile speed score and optimization",
            "endpoint": f"{base_url}/chat/message/"
        },
        {
            "name": "TCPA Optimization",
            "description": "Target CPA optimization recommendations",
            "action": "OPTIMIZE_TCPA",
            "message": "Provide Target CPA optimization recommendations",
            "endpoint": f"{base_url}/chat/message/"
        },
        {
            "name": "Budget Allocation Optimization",
            "description": "Campaign budget allocation optimization",
            "action": "OPTIMIZE_BUDGET_ALLOCATION",
            "message": "Optimize campaign budget allocation",
            "endpoint": f"{base_url}/chat/message/"
        },
        {
            "name": "Negative Keyword Suggestions",
            "description": "Negative keyword exclusion suggestions",
            "action": "SUGGEST_NEGATIVE_KEYWORDS",
            "message": "Suggest negative keyword exclusions",
            "endpoint": f"{base_url}/chat/message/"
        }
    ]
    
    print(f"📊 Total Analysis Actions Available: {len(analysis_actions)}")
    print()
    
    # Display all actions
    for i, action in enumerate(analysis_actions, 1):
        print(f"{i:2d}. {action['name']}")
        print(f"    Description: {action['description']}")
        print(f"    Action: {action['action']}")
        print(f"    Message: {action['message']}")
        print(f"    Endpoint: {action['endpoint']}")
        print()
    
    print("🔧 How to Test These Actions:")
    print("=" * 40)
    print()
    print("1. Start your Django server:")
    print("   python manage.py runserver")
    print()
    print("2. Start your React frontend:")
    print("   npm start")
    print()
    print("3. Get a valid JWT token from your frontend")
    print()
    print("4. Use the chat interface to trigger actions:")
    print("   - Click the action buttons in the chat")
    print("   - Or type the messages directly")
    print()
    print("5. Example API call:")
    print("   curl -X POST http://localhost:8000/google-ads-new/api/chat/message/ \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -H 'Authorization: Bearer YOUR_JWT_TOKEN' \\")
    print("     -d '{\"message\": \"Analyze my audience size, overlap, and quality\", \"session_id\": \"YOUR_SESSION_ID\"}'")
    print()
    
    # Show expected response structure
    print("📋 Expected Response Structure:")
    print("=" * 40)
    print()
    print("Each analysis action will return a response with:")
    print("- success: boolean")
    print("- session_id: string")
    print("- response: object with blocks array")
    print("- intent: object with action, confidence, parameters")
    print()
    print("The response.blocks array will contain AnalysisBlock objects")
    print("that render in the frontend with:")
    print("- Status indicators (info, warning, critical, success)")
    print("- Priority levels (low, medium, high, critical)")
    print("- Detailed recommendations")
    print("- Action items")
    print()
    
    print("🎯 Frontend Integration:")
    print("=" * 40)
    print()
    print("The AnalysisBlock component automatically handles:")
    print("- Different analysis types")
    print("- Status-based styling")
    print("- Priority indicators")
    print("- Recommendation lists")
    print("- Error handling")
    print()
    
    print("✅ All actions are now implemented and ready to use!")
    print("🚀 Happy analyzing!")

if __name__ == "__main__":
    test_analysis_actions()

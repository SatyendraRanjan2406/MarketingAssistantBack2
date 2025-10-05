#!/usr/bin/env python
"""
Example usage of the GOOGLE_ADS_SEARCH tool
"""

import os
import sys
import asyncio
import json

# Add the project directory to Python path
sys.path.insert(0, '/Users/satyendra/marketing_assistant_back')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketing_assistant_project.settings')
import django
django.setup()

from tools import MarketingTools

async def example_usage():
    """Example of how to use the GOOGLE_ADS_SEARCH tool"""
    
    tools = MarketingTools()
    
    # Example 1: Get campaigns with performance metrics
    print("=== Example 1: Campaigns with Performance Metrics ===")
    
    campaign_query = """
    SELECT 
        campaign.id, 
        campaign.name, 
        campaign.status, 
        metrics.impressions, 
        metrics.clicks, 
        metrics.ctr, 
        metrics.conversions, 
        metrics.cost_micros 
    FROM campaign 
    WHERE segments.date DURING LAST_30_DAYS 
    ORDER BY metrics.impressions DESC
    """
    
    result1 = await tools.GOOGLE_ADS_SEARCH({
        "customer_id": "3048406696",
        "query": campaign_query,
        "access_token": "ya29.a0AQQ_BDTrAhNSuriWeucHovdKS17oUvrHOIYGm-8dYet6-eNTcdR9hn8yDv_YLncPEfuOcA8Fe0j2FaGdHRt2XYIUdsEVYrxwg2-0-6BwuH0E7FQhMQXPBRQ2gveX4wsgUmuejqLmlJ4eLYclWl1pW-m1BnmXv5sAAgDk3xq49H-uRgGQaw_bsYb3jqfa0Vt5HdrSwMIaCgYKAVQSARISFQHGX2MiY4AbxEZNXKASvwEJx6MUeg0206"
    })
    
    print(f"Found {result1['total_results']} campaigns")
    for campaign in result1['results']:
        print(f"  - {campaign['campaign_name']} (ID: {campaign['campaign_id']})")
        print(f"    Status: {campaign['campaign_status']}")
        print(f"    Impressions: {campaign['impressions']:,}")
        print(f"    Clicks: {campaign['clicks']:,}")
        print(f"    CTR: {campaign['ctr']:.2%}")
        print(f"    Cost: ${campaign['cost']:.2f}")
        print()
    
    # Example 2: Get ad groups for a specific campaign
    print("=== Example 2: Ad Groups for Campaign ===")
    
    ad_group_query = """
    SELECT 
        ad_group.id, 
        ad_group.name, 
        ad_group.status, 
        campaign.id as campaign_id,
        metrics.impressions, 
        metrics.clicks, 
        metrics.cost_micros 
    FROM ad_group 
    WHERE campaign.id = 22914171797 
    AND segments.date DURING LAST_7_DAYS
    """
    
    result2 = await tools.GOOGLE_ADS_SEARCH({
        "customer_id": "3048406696",
        "query": ad_group_query,
        "access_token": "ya29.a0AQQ_BDTrAhNSuriWeucHovdKS17oUvrHOIYGm-8dYet6-eNTcdR9hn8yDv_YLncPEfuOcA8Fe0j2FaGdHRt2XYIUdsEVYrxwg2-0-6BwuH0E7FQhMQXPBRQ2gveX4wsgUmuejqLmlJ4eLYclWl1pW-m1BnmXv5sAAgDk3xq49H-uRgGQaw_bsYb3jqfa0Vt5HdrSwMIaCgYKAVQSARISFQHGX2MiY4AbxEZNXKASvwEJx6MUeg0206"
    })
    
    print(f"Found {result2['total_results']} ad groups")
    for ad_group in result2['results']:
        print(f"  - {ad_group['ad_group_name']} (ID: {ad_group['ad_group_id']})")
        print(f"    Status: {ad_group['ad_group_status']}")
        print(f"    Impressions: {ad_group['impressions']:,}")
        print(f"    Clicks: {ad_group['clicks']:,}")
        print(f"    Cost: ${ad_group['cost']:.2f}")
        print()
    
    # Example 3: Get keywords with performance
    print("=== Example 3: Keywords with Performance ===")
    
    keyword_query = """
    SELECT 
        keyword_view.resource_name, 
        keyword_view.keyword_text, 
        keyword_view.match_type, 
        metrics.impressions, 
        metrics.clicks, 
        metrics.ctr, 
        metrics.cost_micros 
    FROM keyword_view 
    WHERE segments.date DURING LAST_14_DAYS
    ORDER BY metrics.clicks DESC
    LIMIT 10
    """
    
    result3 = await tools.GOOGLE_ADS_SEARCH({
        "customer_id": "3048406696",
        "query": keyword_query,
        "access_token": "ya29.a0AQQ_BDTrAhNSuriWeucHovdKS17oUvrHOIYGm-8dYet6-eNTcdR9hn8yDv_YLncPEfuOcA8Fe0j2FaGdHRt2XYIUdsEVYrxwg2-0-6BwuH0E7FQhMQXPBRQ2gveX4wsgUmuejqLmlJ4eLYclWl1pW-m1BnmXv5sAAgDk3xq49H-uRgGQaw_bsYb3jqfa0Vt5HdrSwMIaCgYKAVQSARISFQHGX2MiY4AbxEZNXKASvwEJx6MUeg0206"
    })
    
    print(f"Found {result3['total_results']} keywords")
    for keyword in result3['results']:
        print(f"  - '{keyword['keyword_text']}' ({keyword['keyword_match_type']})")
        print(f"    Impressions: {keyword['impressions']:,}")
        print(f"    Clicks: {keyword['clicks']:,}")
        print(f"    CTR: {keyword['ctr']:.2%}")
        print(f"    Cost: ${keyword['cost']:.2f}")
        print()

if __name__ == "__main__":
    asyncio.run(example_usage())

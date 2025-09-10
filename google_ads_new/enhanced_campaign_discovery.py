"""
Enhanced Campaign Discovery Service for Google Ads Chat System
Implements fuzzy matching, semantic search, and campaign discovery
"""

import logging
from typing import Dict, List, Any, Optional
from difflib import SequenceMatcher
from django.contrib.auth.models import User
from .models import GoogleAdsCampaign

logger = logging.getLogger(__name__)

class EnhancedCampaignDiscoveryService:
    """Enhanced campaign discovery using fuzzy matching and semantic search"""
    
    def __init__(self, user: User):
        self.user = user
        self.fuzzy_threshold = 80  # Minimum fuzzy match score
    
    def find_campaigns_by_context(self, context: str, user: User) -> List[Dict]:
        """Find campaigns using multiple discovery strategies"""
        try:
            campaigns = []
            
            # Strategy 1: Exact name match
            exact_matches = self._find_exact_matches(context)
            campaigns.extend(exact_matches)
            
            # Strategy 2: Fuzzy string matching
            fuzzy_matches = self._find_fuzzy_matches(context)
            campaigns.extend(fuzzy_matches)
            
            # Strategy 3: Semantic similarity (business category matching)
            semantic_matches = self._find_semantic_matches(context)
            campaigns.extend(semantic_matches)
            
            # Strategy 4: Partial word matching
            partial_matches = self._find_partial_matches(context)
            campaigns.extend(partial_matches)
            
            # Remove duplicates and sort by relevance score
            unique_campaigns = self._deduplicate_campaigns(campaigns)
            sorted_campaigns = sorted(unique_campaigns, key=lambda x: x['relevance_score'], reverse=True)
            
            logger.info(f"Found {len(sorted_campaigns)} campaigns for context: {context}")
            return sorted_campaigns
            
        except Exception as e:
            logger.error(f"Error finding campaigns by context: {e}")
            return []
    
    def _find_exact_matches(self, context: str) -> List[Dict]:
        """Find campaigns with exact name matches"""
        exact_matches = []
        
        try:
            # Get all campaigns for the user
            campaigns = GoogleAdsCampaign.objects.filter(
                google_ads_account__user=self.user
            ).values('id', 'name', 'status', 'budget_amount', 'start_date', 'end_date')
            
            context_lower = context.lower().strip()
            
            for campaign in campaigns:
                campaign_name_lower = campaign['name'].lower().strip()
                
                if context_lower == campaign_name_lower:
                    exact_matches.append({
                        'campaign': campaign,
                        'match_score': 100,
                        'match_type': 'exact',
                        'relevance_score': 100,
                        'campaign_id': campaign['id'],
                        'campaign_name': campaign['name'],
                        'status': campaign['status'],
                        'budget': campaign['budget_amount'],
                        'start_date': campaign['start_date'],
                        'end_date': campaign['end_date']
                    })
            
            logger.info(f"Found {len(exact_matches)} exact matches")
            return exact_matches
            
        except Exception as e:
            logger.error(f"Error finding exact matches: {e}")
            return []
    
    def _find_fuzzy_matches(self, context: str) -> List[Dict]:
        """Find campaigns using fuzzy string matching"""
        fuzzy_matches = []
        
        try:
            # Get all campaigns for the user
            campaigns = GoogleAdsCampaign.objects.filter(
                google_ads_account__user=self.user
            ).values('id', 'name', 'status', 'budget_amount', 'start_date', 'end_date')
            
            context_lower = context.lower().strip()
            
            for campaign in campaigns:
                campaign_name_lower = campaign['name'].lower().strip()
                
                # Multiple fuzzy matching strategies
                partial_ratio = fuzz.partial_ratio(context_lower, campaign_name_lower)
                token_sort_ratio = fuzz.token_sort_ratio(context_lower, campaign_name_lower)
                token_set_ratio = fuzz.token_set_ratio(context_lower, campaign_name_lower)
                
                # Use the highest score
                fuzzy_score = max(partial_ratio, token_sort_ratio, token_set_ratio)
                
                if fuzzy_score >= self.fuzzy_threshold:
                    fuzzy_matches.append({
                        'campaign': campaign,
                        'match_score': fuzzy_score,
                        'match_type': 'fuzzy',
                        'relevance_score': fuzzy_score * 0.9,  # Slightly lower than exact
                        'campaign_id': campaign['id'],
                        'campaign_name': campaign['name'],
                        'status': campaign['status'],
                        'budget': campaign['budget_amount'],
                        'start_date': campaign['start_date'],
                        'end_date': campaign['end_date']
                    })
            
            logger.info(f"Found {len(fuzzy_matches)} fuzzy matches")
            return fuzzy_matches
            
        except Exception as e:
            logger.error(f"Error finding fuzzy matches: {e}")
            return []
    
    def _find_semantic_matches(self, context: str) -> List[Dict]:
        """Find campaigns using semantic similarity (business category matching)"""
        semantic_matches = []
        
        try:
            # Business category mapping
            business_categories = {
                'education': ['course', 'training', 'learning', 'education', 'school', 'university', 'academy'],
                'ecommerce': ['shop', 'store', 'buy', 'purchase', 'product', 'service', 'retail'],
                'b2b': ['business', 'enterprise', 'corporate', 'professional', 'consulting', 'agency'],
                'healthcare': ['health', 'medical', 'doctor', 'clinic', 'hospital', 'wellness', 'fitness'],
                'technology': ['software', 'app', 'digital', 'tech', 'platform', 'solution', 'system']
            }
            
            # Determine business category from context
            context_lower = context.lower().strip()
            detected_category = None
            
            for category, keywords in business_categories.items():
                for keyword in keywords:
                    if keyword in context_lower:
                        detected_category = category
                        break
                if detected_category:
                    break
            
            if detected_category:
                # Find campaigns that match the business category
                campaigns = GoogleAdsCampaign.objects.filter(
                    google_ads_account__user=self.user
                ).values('id', 'name', 'status', 'budget_amount', 'start_date', 'end_date')
                
                for campaign in campaigns:
                    campaign_name_lower = campaign['name'].lower().strip()
                    
                    # Check if campaign name contains category keywords
                    category_keywords = business_categories[detected_category]
                    category_match = any(keyword in campaign_name_lower for keyword in category_keywords)
                    
                    if category_match:
                        semantic_matches.append({
                            'campaign': campaign,
                            'match_score': 85,  # High semantic relevance
                            'match_type': 'semantic',
                            'relevance_score': 85,
                            'campaign_id': campaign['id'],
                            'campaign_name': campaign['name'],
                            'status': campaign['status'],
                            'budget': campaign['budget_amount'],
                            'start_date': campaign['start_date'],
                            'end_date': campaign['end_date'],
                            'business_category': detected_category
                        })
            
            logger.info(f"Found {len(semantic_matches)} semantic matches")
            return semantic_matches
            
        except Exception as e:
            logger.error(f"Error finding semantic matches: {e}")
            return []
    
    def _find_partial_matches(self, context: str) -> List[Dict]:
        """Find campaigns using partial word matching"""
        partial_matches = []
        
        try:
            # Get all campaigns for the user
            campaigns = GoogleAdsCampaign.objects.filter(
                google_ads_account__user=self.user
            ).values('id', 'name', 'status', 'budget_amount', 'start_date', 'end_date')
            
            context_words = context.lower().strip().split()
            
            for campaign in campaigns:
                campaign_name_words = campaign['name'].lower().strip().split()
                
                # Count matching words
                matching_words = 0
                total_context_words = len(context_words)
                
                for context_word in context_words:
                    if len(context_word) > 2:  # Only consider words longer than 2 characters
                        for campaign_word in campaign_name_words:
                            if context_word in campaign_word or campaign_word in context_word:
                                matching_words += 1
                                break
                
                # Calculate partial match score
                if total_context_words > 0:
                    partial_score = (matching_words / total_context_words) * 100
                    
                    if partial_score >= 60:  # At least 60% word match
                        partial_matches.append({
                            'campaign': campaign,
                            'match_score': partial_score,
                            'match_type': 'partial',
                            'relevance_score': partial_score * 0.8,  # Lower than fuzzy
                            'campaign_id': campaign['id'],
                            'campaign_name': campaign['name'],
                            'status': campaign['status'],
                            'budget': campaign['budget_amount'],
                            'start_date': campaign['start_date'],
                            'end_date': campaign['end_date'],
                            'matching_words': matching_words,
                            'total_words': total_context_words
                        })
            
            logger.info(f"Found {len(partial_matches)} partial matches")
            return partial_matches
            
        except Exception as e:
            logger.error(f"Error finding partial matches: {e}")
            return []
    
    def _deduplicate_campaigns(self, campaigns: List[Dict]) -> List[Dict]:
        """Remove duplicate campaigns and keep the best match"""
        seen_campaign_ids = set()
        unique_campaigns = []
        
        for campaign in campaigns:
            campaign_id = campaign['campaign_id']
            
            if campaign_id not in seen_campaign_ids:
                seen_campaign_ids.add(campaign_id)
                unique_campaigns.append(campaign)
            else:
                # If we already have this campaign, keep the one with higher relevance score
                existing_campaign = next(c for c in unique_campaigns if c['campaign_id'] == campaign_id)
                if campaign['relevance_score'] > existing_campaign['relevance_score']:
                    # Replace the existing campaign
                    unique_campaigns.remove(existing_campaign)
                    unique_campaigns.append(campaign)
        
        return unique_campaigns
    
    def get_campaigns_by_status(self, status: str = 'all') -> List[Dict]:
        """Get campaigns filtered by status"""
        try:
            if status == 'all':
                campaigns = GoogleAdsCampaign.objects.filter(
                    google_ads_account__user=self.user
                )
            elif status == 'enabled':
                campaigns = GoogleAdsCampaign.objects.filter(
                    google_ads_account__user=self.user,
                    status='ENABLED'
                )
            elif status == 'paused':
                campaigns = GoogleAdsCampaign.objects.filter(
                    google_ads_account__user=self.user,
                    status='PAUSED'
                )
            else:
                campaigns = GoogleAdsCampaign.objects.filter(
                    google_ads_account__user=self.user
                )
            
            campaign_list = []
            for campaign in campaigns:
                campaign_list.append({
                    'campaign_id': campaign.id,
                    'campaign_name': campaign.name,
                    'status': campaign.status,
                    'budget': campaign.budget_amount,
                    'start_date': campaign.start_date,
                    'end_date': campaign.end_date
                })
            
            logger.info(f"Retrieved {len(campaign_list)} campaigns with status: {status}")
            return campaign_list
            
        except Exception as e:
            logger.error(f"Error getting campaigns by status: {e}")
            return []
    
    def extract_campaign_mentions(self, user_message: str) -> List[str]:
        """Extract potential campaign names from natural language"""
        import re
        
        # Common campaign patterns
        patterns = [
            r'my\s+([a-zA-Z\s]+?)\s+campaign',
            r'the\s+([a-zA-Z\s]+?)\s+campaign',
            r'([a-zA-Z\s]+?)\s+campaign',
            r'campaign\s+([a-zA-Z\s]+?)',
            r'([a-zA-Z\s]+?)\s+ads',
            r'([a-zA-Z\s]+?)\s+marketing'
        ]
        
        campaign_mentions = []
        for pattern in patterns:
            matches = re.findall(pattern, user_message, re.IGNORECASE)
            for match in matches:
                if match.strip() and len(match.strip()) > 2:
                    campaign_mentions.append(match.strip())
        
        return list(set(campaign_mentions))

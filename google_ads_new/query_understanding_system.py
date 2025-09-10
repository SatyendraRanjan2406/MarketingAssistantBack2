"""
Enhanced Query Understanding System for Google AI Chatbot
Implements semantic understanding, context awareness, and intelligent parameter extraction
"""

import os
import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from django.contrib.auth.models import User
from django.db.models import Q, Sum, Avg, Count
from difflib import SequenceMatcher
from django.utils import timezone
from .models import (
    GoogleAdsAccount, GoogleAdsCampaign, GoogleAdsAdGroup, 
    GoogleAdsKeyword, GoogleAdsPerformance
)
from .openai_service import GoogleAdsOpenAIService

logger = logging.getLogger(__name__)

try:
    from fuzzywuzzy import fuzz
    FUZZY_AVAILABLE = True
except ImportError:
    FUZZY_AVAILABLE = False
    logger.warning("fuzzywuzzy not available, using basic string matching")


class ContextExtractor:
    """Extract context from user queries using AI and pattern matching"""
    
    def __init__(self):
        self.openai_service = GoogleAdsOpenAIService()
    
    def extract_context(self, user_message: str, user: User) -> Dict[str, Any]:
        """Extract comprehensive context from user message"""
        try:
            context = {
                'business_entities': [],
                'time_periods': [],
                'metrics': [],
                'business_objectives': [],
                'target_audiences': [],
                'campaign_mentions': [],
                'account_mentions': [],
                'keyword_mentions': [],
                'business_category': None,
                'extracted_parameters': {}
            }
            
            # Extract using multiple methods
            context.update(self._extract_patterns(user_message))
            context.update(self._extract_ai_context(user_message))
            context.update(self._extract_campaign_mentions(user_message, user))
            context.update(self._extract_account_mentions(user_message, user))
            
            return context
            
        except Exception as e:
            logger.error(f"Error extracting context: {e}")
            return {'error': f"Context extraction failed: {str(e)}"}
    
    def _extract_patterns(self, user_message: str) -> Dict[str, Any]:
        """Extract patterns using regex and basic NLP"""
        patterns = {}
        
        # Time periods
        time_patterns = {
            'last_7_days': r'last\s+(?:7|seven)\s+days?',
            'last_30_days': r'last\s+(?:30|thirty)\s+days?',
            'this_month': r'this\s+month',
            'this_quarter': r'this\s+quarter',
            'this_year': r'this\s+year',
            'yesterday': r'yesterday',
            'today': r'today'
        }
        
        for period, pattern in time_patterns.items():
            if re.search(pattern, user_message.lower()):
                patterns['time_periods'] = patterns.get('time_periods', []) + [period]
        
        # Metrics
        metric_patterns = {
            'ROAS': r'\b(?:ROAS|roas|return\s+on\s+ad\s+spend)\b',
            'CTR': r'\b(?:CTR|ctr|click.?through\s+rate)\b',
            'CPC': r'\b(?:CPC|cpc|cost\s+per\s+click)\b',
            'CPM': r'\b(?:CPM|cpm|cost\s+per\s+thousand)\b',
            'conversions': r'\b(?:conversions?|conversion\s+rate)\b',
            'impressions': r'\b(?:impressions?|impression\s+share)\b',
            'clicks': r'\b(?:clicks?|click\s+volume)\b'
        }
        
        for metric, pattern in metric_patterns.items():
            if re.search(pattern, user_message.lower()):
                patterns['metrics'] = patterns.get('metrics', []) + [metric]
        
        # Business objectives
        objective_patterns = {
            'improve': r'\b(?:improve|enhance|boost|increase|optimize)\b',
            'analyze': r'\b(?:analyze|analysis|examine|review|assess)\b',
            'compare': r'\b(?:compare|comparison|vs|versus)\b',
            'suggest': r'\b(?:suggest|recommend|propose|advise)\b',
            'generate': r'\b(?:generate|create|develop|build)\b'
        }
        
        for objective, pattern in objective_patterns.items():
            if re.search(pattern, user_message.lower()):
                patterns['business_objectives'] = patterns.get('business_objectives', []) + [objective]
        
        return patterns
    
    def _extract_ai_context(self, user_message: str) -> Dict[str, Any]:
        """Use AI to extract business context and entities"""
        try:
            prompt = f"""
            Analyze this user query and extract business context:
            Query: "{user_message}"
            
            Extract and return JSON with:
            - business_category: Main business category (Education, E-commerce, B2B, etc.)
            - target_audience: Target audience characteristics
            - business_entities: Business names, products, services mentioned
            - industry_keywords: Industry-specific terms
            
            Return only valid JSON.
            """
            
            response = self.openai_service.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a business context analyzer. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=300
            )
            
            content = response.choices[0].message.content
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                import json
                return json.loads(json_match.group())
            
            return {}
            
        except Exception as e:
            logger.error(f"AI context extraction failed: {e}")
            return {}
    
    def _extract_campaign_mentions(self, user_message: str, user: User) -> Dict[str, Any]:
        """Extract potential campaign names from user message"""
        try:
            # Get user's campaigns
            campaigns = GoogleAdsCampaign.objects.filter(
                account__user=user,
                account__is_active=True
            ).values('id', 'campaign_name', 'campaign_status')
            
            campaign_mentions = []
            
            for campaign in campaigns:
                campaign_name = campaign['campaign_name'].lower()
                user_message_lower = user_message.lower()
                
                # Check for exact matches or partial matches
                if (campaign_name in user_message_lower or 
                    user_message_lower in campaign_name or
                    any(word in user_message_lower for word in campaign_name.split())):
                    
                    campaign_mentions.append({
                        'campaign_id': campaign['id'],
                        'campaign_name': campaign['campaign_name'],
                        'campaign_status': campaign['campaign_status'],
                        'match_type': 'exact' if campaign_name in user_message_lower else 'partial',
                        'match_score': 1.0 if campaign_name in user_message_lower else 0.8
                    })
            
            return {'campaign_mentions': campaign_mentions}
            
        except Exception as e:
            logger.error(f"Campaign mention extraction failed: {e}")
            return {'campaign_mentions': []}
    
    def _extract_account_mentions(self, user_message: str, user: User) -> Dict[str, Any]:
        """Extract account references from user message"""
        try:
            accounts = GoogleAdsAccount.objects.filter(
                user=user,
                is_active=True
            ).values('id', 'account_name', 'customer_id')
            
            account_mentions = []
            
            for account in accounts:
                account_name = account['account_name'].lower()
                user_message_lower = user_message.lower()
                
                if (account_name in user_message_lower or
                    account['customer_id'] in user_message):
                    
                    account_mentions.append({
                        'account_id': account['id'],
                        'account_name': account['account_name'],
                        'customer_id': account['customer_id'],
                        'match_type': 'exact'
                    })
            
            return {'account_mentions': account_mentions}
            
        except Exception as e:
            logger.error(f"Account mention extraction failed: {e}")
            return {'account_mentions': []}


class CampaignDiscoveryService:
    """Find campaigns using fuzzy matching and semantic search"""
    
    def __init__(self, user: User):
        self.user = user
    
    def find_campaigns_by_context(self, context: str, status_filter: str = "all") -> List[Dict]:
        """Find campaigns using multiple matching strategies"""
        try:
            # Get user's campaigns with status filtering
            campaigns_query = GoogleAdsCampaign.objects.filter(
                account__user=self.user,
                account__is_active=True
            )
            
            if status_filter == "enabled":
                campaigns_query = campaigns_query.filter(campaign_status='ENABLED')
            elif status_filter == "paused":
                campaigns_query = campaigns_query.filter(campaign_status='PAUSED')
            # "all" includes all statuses
            
            campaigns = campaigns_query.select_related('account').values(
                'id', 'campaign_id', 'campaign_name', 'campaign_status',
                'campaign_type', 'budget_amount', 'account__account_name'
            )
            
            if not campaigns.exists():
                return []
            
            # Find similar campaigns using fuzzy matching
            similar_campaigns = self._find_similar_campaigns(context, list(campaigns))
            
            return similar_campaigns
            
        except Exception as e:
            logger.error(f"Campaign discovery failed: {e}")
            return []
    
    def _find_similar_campaigns(self, query: str, campaigns: List[Dict]) -> List[Dict]:
        """Find campaigns using fuzzy matching"""
        similar_campaigns = []
        query_lower = query.lower()
        
        for campaign in campaigns:
            campaign_name = campaign['campaign_name'].lower()
            
            # Multiple matching strategies
            exact_match = query_lower in campaign_name or campaign_name in query_lower
            word_match = any(word in campaign_name for word in query_lower.split())
            
            if FUZZY_AVAILABLE:
                fuzzy_score = fuzz.partial_ratio(query_lower, campaign_name)
                token_sort_score = fuzz.token_sort_ratio(query_lower, campaign_name)
                token_set_score = fuzz.token_set_ratio(query_lower, campaign_name)
                
                max_fuzzy_score = max(fuzzy_score, token_sort_score, token_set_score)
            else:
                # Basic similarity using difflib
                max_fuzzy_score = SequenceMatcher(None, query_lower, campaign_name).ratio() * 100
            
            # Determine match type and score
            if exact_match:
                match_type = 'exact'
                match_score = 100
            elif word_match:
                match_type = 'word_match'
                match_score = 85
            elif max_fuzzy_score > 70:
                match_type = 'fuzzy'
                match_score = max_fuzzy_score
            else:
                continue  # Skip low similarity matches
            
            similar_campaigns.append({
                'campaign': campaign,
                'match_score': match_score,
                'match_type': match_type,
                'relevance': self._calculate_relevance(campaign, query_lower)
            })
        
        # Sort by relevance and match score
        similar_campaigns.sort(key=lambda x: (x['relevance'], x['match_score']), reverse=True)
        
        return similar_campaigns
    
    def _calculate_relevance(self, campaign: Dict, query: str) -> float:
        """Calculate campaign relevance based on multiple factors"""
        relevance = 0.0
        
        # Campaign status relevance
        if campaign['campaign_status'] == 'ENABLED':
            relevance += 20
        elif campaign['campaign_status'] == 'PAUSED':
            relevance += 10
        
        # Campaign type relevance
        campaign_type = campaign['campaign_type'].lower()
        if 'search' in query and campaign_type == 'SEARCH':
            relevance += 15
        elif 'display' in query and campaign_type == 'DISPLAY':
            relevance += 15
        elif 'video' in query and campaign_type == 'VIDEO':
            relevance += 15
        
        # Budget relevance (higher budget = higher relevance for optimization queries)
        if 'optimize' in query or 'improve' in query:
            if campaign.get('budget_amount', 0) > 100:
                relevance += 10
        
        return relevance
    
    def extract_campaign_mentions(self, user_message: str) -> List[str]:
        """Extract potential campaign names from natural language"""
        try:
            # Use AI to extract campaign mentions
            prompt = f"""
            Extract potential campaign names from this user message:
            "{user_message}"
            
            Return a JSON array of campaign names or business entities that could be campaigns.
            Example: ["Digital Marketing Course", "Summer Sale", "Product Launch"]
            """
            
            openai_service = GoogleAdsOpenAIService()
            response = openai_service.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Extract campaign names as JSON array or all campaigns if no names detected"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=200
            )
            
            content = response.choices[0].message.content
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                import json
                return json.loads(json_match.group())
            
            return []
            
        except Exception as e:
            logger.error(f"Campaign mention extraction failed: {e}")
            return []


class KeywordIntelligenceTools:
    """Generate and analyze keywords for campaigns"""
    
    def __init__(self, user: User):
        self.user = user
        self.openai_service = GoogleAdsOpenAIService()
    
    def suggest_keywords_for_campaign(self, campaign_id: int, 
                                   business_context: str, 
                                   target_audience: str) -> Dict[str, Any]:
        """Generate keyword suggestions for a campaign"""
        try:
            # Get campaign details
            campaign = GoogleAdsCampaign.objects.select_related('account').get(
                id=campaign_id,
                account__user=self.user
            )
            
            # Get existing keywords
            existing_keywords = GoogleAdsKeyword.objects.filter(
                ad_group__campaign_id=campaign_id
            ).values('keyword_text', 'match_type', 'status')
            
            # Generate new keyword suggestions using AI
            keyword_suggestions = self._generate_ai_keywords(
                campaign_name=campaign.campaign_name,
                business_context=business_context,
                target_audience=target_audience,
                existing_keywords=[k['keyword_text'] for k in existing_keywords]
            )
            
            # Analyze keyword opportunities
            opportunities = self._analyze_keyword_opportunities(campaign_id)
            
            return {
                'campaign_name': campaign.campaign_name,
                'business_context': business_context,
                'target_audience': target_audience,
                'existing_keywords': list(existing_keywords),
                'new_keyword_suggestions': keyword_suggestions,
                'keyword_opportunities': opportunities,
                'recommendations': self._generate_keyword_recommendations(
                    existing_keywords, keyword_suggestions, opportunities
                )
            }
            
        except Exception as e:
            logger.error(f"Keyword suggestion failed: {e}")
            return {'error': f"Keyword suggestion failed: {str(e)}"}
    
    def _generate_ai_keywords(self, campaign_name: str, business_context: str, 
                             target_audience: str, existing_keywords: List[str]) -> List[Dict]:
        """Generate keywords using AI"""
        try:
            prompt = f"""
            Generate keyword suggestions for a Google Ads campaign:
            
            Campaign Name: {campaign_name}
            Business Context: {business_context}
            Target Audience: {target_audience}
            Existing Keywords: {', '.join(existing_keywords[:10])}
            
            Generate 20 new keyword suggestions with:
            - Keyword text
            - Suggested match type (EXACT, PHRASE, BROAD)
            - Reasoning for the suggestion
            - Expected performance level (High/Medium/Low)
            
            Return as JSON array with objects containing: keyword, match_type, reasoning, performance_level
            """
            
            response = self.openai_service.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Generate keyword suggestions as JSON array"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            content = response.choices[0].message.content
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                import json
                return json.loads(json_match.group())
            
            return []
            
        except Exception as e:
            logger.error(f"AI keyword generation failed: {e}")
            return []
    
    def _analyze_keyword_opportunities(self, campaign_id: int) -> Dict[str, Any]:
        """Analyze keyword opportunities and gaps"""
        try:
            # Get keyword performance data
            keyword_performance = GoogleAdsPerformance.objects.filter(
                keyword__ad_group__campaign_id=campaign_id
            ).select_related('keyword').values(
                'keyword__keyword_text',
                'keyword__quality_score',
                'impressions',
                'clicks',
                'cost_micros',
                'conversions',
                'conversion_value'
            )
            
            opportunities = {
                'high_performing_keywords': [],
                'underperforming_keywords': [],
                'keyword_gaps': [],
                'bid_optimization': []
            }
            
            for perf in keyword_performance:
                if perf['impressions'] > 0:
                    ctr = perf['clicks'] / perf['impressions']
                    cpc = (perf['cost_micros'] / 1000000) / perf['clicks'] if perf['clicks'] > 0 else 0
                    roas = (perf['conversion_value'] / (perf['cost_micros'] / 1000000)) if perf['cost_micros'] > 0 else 0
                    
                    keyword_data = {
                        'keyword': perf['keyword__keyword_text'],
                        'quality_score': perf['keyword__quality_score'],
                        'ctr': ctr,
                        'cpc': cpc,
                        'roas': roas,
                        'impressions': perf['impressions']
                    }
                    
                    # Categorize keywords
                    if roas > 3.0 and ctr > 0.02:
                        opportunities['high_performing_keywords'].append(keyword_data)
                    elif roas < 1.0 or ctr < 0.005:
                        opportunities['underperforming_keywords'].append(keyword_data)
                    
                    # Bid optimization suggestions
                    if roas > 4.0 and perf['impressions'] < 1000:
                        opportunities['bid_optimization'].append({
                            'keyword': perf['keyword__keyword_text'],
                            'action': 'increase_bid',
                            'reason': 'High ROAS, low impressions'
                        })
                    elif roas < 0.5 and perf['impressions'] > 5000:
                        opportunities['bid_optimization'].append({
                            'keyword': perf['keyword__keyword_text'],
                            'action': 'decrease_bid',
                            'reason': 'Low ROAS, high spend'
                        })
            
            return opportunities
            
        except Exception as e:
            logger.error(f"Keyword opportunity analysis failed: {e}")
            return {'error': f"Analysis failed: {str(e)}"}
    
    def _generate_keyword_recommendations(self, existing_keywords: List[Dict], 
                                        new_suggestions: List[Dict], 
                                        opportunities: Dict) -> List[str]:
        """Generate actionable keyword recommendations"""
        recommendations = []
        
        # Based on existing keywords
        if len(existing_keywords) < 10:
            recommendations.append("Consider adding more keywords to improve campaign coverage")
        
        # Based on new suggestions
        if new_suggestions:
            high_perf_suggestions = [s for s in new_suggestions if s.get('performance_level') == 'High']
            if high_perf_suggestions:
                recommendations.append(f"Prioritize adding {len(high_perf_suggestions)} high-performance keyword suggestions")
        
        # Based on opportunities
        if opportunities.get('underperforming_keywords'):
            recommendations.append(f"Review and optimize {len(opportunities['underperforming_keywords'])} underperforming keywords")
        
        if opportunities.get('bid_optimization'):
            recommendations.append(f"Consider {len(opportunities['bid_optimization'])} bid adjustments for better performance")
        
        return recommendations


class ParameterExtractor:
    """Extract parameters from natural language queries"""
    
    def __init__(self):
        self.openai_service = GoogleAdsOpenAIService()
    
    def extract_parameters(self, user_message: str, context: Dict) -> Dict[str, Any]:
        """Extract comprehensive parameters from user query"""
        try:
            # Extract using multiple methods
            basic_params = self._extract_basic_parameters(user_message)
            ai_params = self._extract_ai_parameters(user_message, context)
            
            # Merge parameters
            all_params = {**basic_params, **ai_params}
            
            # Validate and clean parameters
            cleaned_params = self._clean_parameters(all_params)
            
            return cleaned_params
            
        except Exception as e:
            logger.error(f"Parameter extraction failed: {e}")
            return {}
    
    def _extract_basic_parameters(self, user_message: str) -> Dict[str, Any]:
        """Extract parameters using pattern matching"""
        params = {}
        
        # Campaign status
        if 'enabled' in user_message.lower():
            params['campaign_status'] = 'ENABLED'
        elif 'paused' in user_message.lower():
            params['campaign_status'] = 'PAUSED'
        elif 'all' in user_message.lower() and 'campaign' in user_message.lower():
            params['campaign_status'] = 'ALL'
        
        # Time periods
        if 'last 7 days' in user_message.lower():
            params['time_period'] = 'last_7_days'
        elif 'last 30 days' in user_message.lower():
            params['time_period'] = 'last_30_days'
        elif 'this month' in user_message.lower():
            params['time_period'] = 'this_month'
        
        # Metrics
        metrics = []
        if 'roas' in user_message.lower():
            metrics.append('ROAS')
        if 'ctr' in user_message.lower():
            metrics.append('CTR')
        if 'cpc' in user_message.lower():
            metrics.append('CPC')
        if 'conversions' in user_message.lower():
            metrics.append('conversions')
        
        if metrics:
            params['metrics'] = metrics
        
        return params
    
    def _extract_ai_parameters(self, user_message: str, context: Dict) -> Dict[str, Any]:
        """Use AI to extract complex parameters"""
        try:
            prompt = f"""
            Extract parameters from this user query:
            "{user_message}"
            
            Context: {context}
            
            Extract and return JSON with:
            - campaign_names: List of campaign names mentioned
            - business_objectives: What the user wants to achieve
            - target_metrics: Specific metrics they want to improve
            - time_constraints: Any time-related constraints
            - audience_targeting: Target audience information
            - budget_constraints: Budget-related parameters
            
            Return only valid JSON.
            """
            
            response = self.openai_service.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Extract parameters as JSON"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=400
            )
            
            content = response.choices[0].message.content
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                import json
                return json.loads(json_match.group())
            
            return {}
            
        except Exception as e:
            logger.error(f"AI parameter extraction failed: {e}")
            return {}
    
    def _clean_parameters(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and validate extracted parameters"""
        cleaned = {}
        
        for key, value in params.items():
            if value is not None and value != "":
                if isinstance(value, list) and len(value) > 0:
                    cleaned[key] = value
                elif isinstance(value, str) and value.strip():
                    cleaned[key] = value.strip()
                elif isinstance(value, (int, float)):
                    cleaned[key] = value
        
        return cleaned


class QueryUnderstandingPipeline:
    """Multi-stage query understanding and processing"""
    
    def __init__(self, user: User):
        self.user = user
        self.context_extractor = ContextExtractor()
        self.campaign_discovery = CampaignDiscoveryService(user)
        self.parameter_extractor = ParameterExtractor()
        self.keyword_intelligence = KeywordIntelligenceTools(user)
        self.openai_service = GoogleAdsOpenAIService()
    
    def process_query(self, user_message: str) -> Dict[str, Any]:
        """Process query through multiple understanding stages"""
        try:
            # Stage 1: Context Extraction
            context = self.context_extractor.extract_context(user_message, self.user)
            
            # Stage 2: Campaign Discovery
            campaigns = self._discover_campaigns(context, user_message)
            
            # Stage 3: Parameter Extraction
            parameters = self.parameter_extractor.extract_parameters(user_message, context)
            
            # Stage 4: Business Context Analysis
            business_context = self._analyze_business_context(campaigns, context)
            
            # Stage 5: Tool Selection
            tools = self._select_tools(user_message, context, campaigns, parameters)
            
            return {
                'success': True,
                'context': context,
                'campaigns': campaigns,
                'parameters': parameters,
                'business_context': business_context,
                'tools': tools,
                'query_understanding': {
                    'stage': 'completed',
                    'confidence': self._calculate_confidence(context, campaigns, parameters)
                }
            }
            
        except Exception as e:
            logger.error(f"Query understanding pipeline failed: {e}")
            return self._handle_pipeline_error(user_message, str(e))
    
    def _discover_campaigns(self, context: Dict, user_message: str) -> List[Dict]:
        """Discover campaigns based on context and user message"""
        try:
            # Extract campaign mentions from user message
            campaign_mentions = self.campaign_discovery.extract_campaign_mentions(user_message)
            
            discovered_campaigns = []
            
            # Search for campaigns mentioned in user message
            for mention in campaign_mentions:
                campaigns = self.campaign_discovery.find_campaigns_by_context(mention)
                discovered_campaigns.extend(campaigns)
            
            # Also search using the full context
            if context.get('business_entities'):
                for entity in context['business_entities']:
                    campaigns = self.campaign_discovery.find_campaigns_by_context(entity)
                    discovered_campaigns.extend(campaigns)
            
            # Remove duplicates and sort by relevance
            unique_campaigns = {}
            for campaign_data in discovered_campaigns:
                campaign_id = campaign_data['campaign']['id']
                if campaign_id not in unique_campaigns:
                    unique_campaigns[campaign_id] = campaign_data
                else:
                    # Keep the one with higher relevance
                    if campaign_data['relevance'] > unique_campaigns[campaign_id]['relevance']:
                        unique_campaigns[campaign_id] = campaign_data
            
            return list(unique_campaigns.values())
            
        except Exception as e:
            logger.error(f"Campaign discovery failed: {e}")
            return []
    
    def _analyze_business_context(self, campaigns: List[Dict], context: Dict) -> Dict[str, Any]:
        """Analyze business context based on discovered campaigns"""
        try:
            business_context = {
                'business_category': context.get('business_category'),
                'target_audience': context.get('target_audience'),
                'industry_keywords': context.get('industry_keywords', []),
                'campaign_insights': []
            }
            
            # Analyze each discovered campaign
            for campaign_data in campaigns:
                campaign = campaign_data['campaign']
                
                # Get campaign performance insights
                performance = self._get_campaign_performance_insights(campaign['id'])
                
                campaign_insight = {
                    'campaign_id': campaign['id'],
                    'campaign_name': campaign['campaign_name'],
                    'campaign_status': campaign['campaign_status'],
                    'campaign_type': campaign['campaign_type'],
                    'performance_summary': performance,
                    'keyword_count': self._get_campaign_keyword_count(campaign['id']),
                    'optimization_opportunities': self._identify_optimization_opportunities(campaign['id'])
                }
                
                business_context['campaign_insights'].append(campaign_insight)
            
            return business_context
            
        except Exception as e:
            logger.error(f"Business context analysis failed: {e}")
            return {'error': f"Business context analysis failed: {str(e)}"}
    
    def _get_campaign_performance_insights(self, campaign_id: int) -> Dict[str, Any]:
        """Get performance insights for a campaign"""
        try:
            # Get recent performance data
            performance_data = GoogleAdsPerformance.objects.filter(
                campaign_id=campaign_id
            ).aggregate(
                total_impressions=Sum('impressions'),
                total_clicks=Sum('clicks'),
                total_cost=Sum('cost_micros'),
                total_conversions=Sum('conversions'),
                total_conversion_value=Sum('conversion_value')
            )
            
            if performance_data['total_impressions'] and performance_data['total_impressions'] > 0:
                ctr = performance_data['total_clicks'] / performance_data['total_impressions']
                cpc = (performance_data['total_cost'] / 1000000) / performance_data['total_clicks'] if performance_data['total_clicks'] > 0 else 0
                roas = (performance_data['total_conversion_value'] / (performance_data['total_cost'] / 1000000)) if performance_data['total_cost'] > 0 else 0
                
                return {
                    'impressions': performance_data['total_impressions'],
                    'clicks': performance_data['total_clicks'],
                    'cost': performance_data['total_cost'] / 1000000,
                    'conversions': performance_data['total_conversions'],
                    'conversion_value': performance_data['total_conversion_value'],
                    'ctr': ctr,
                    'cpc': cpc,
                    'roas': roas
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"Performance insights failed: {e}")
            return {}
    
    def _get_campaign_keyword_count(self, campaign_id: int) -> int:
        """Get keyword count for a campaign"""
        try:
            return GoogleAdsKeyword.objects.filter(
                ad_group__campaign_id=campaign_id
            ).count()
        except Exception as e:
            logger.error(f"Keyword count failed: {e}")
            return 0
    
    def _identify_optimization_opportunities(self, campaign_id: int) -> List[str]:
        """Identify optimization opportunities for a campaign"""
        try:
            opportunities = []
            
            # Check keyword performance
            keyword_performance = GoogleAdsPerformance.objects.filter(
                keyword__ad_group__campaign_id=campaign_id
            ).aggregate(
                avg_quality_score=Avg('keyword__quality_score'),
                low_ctr_keywords=Count('id')
            )
            
            if keyword_performance['avg_quality_score'] and keyword_performance['avg_quality_score'] < 5:
                opportunities.append("Improve keyword quality scores")
            
            if keyword_performance['low_ctr_keywords'] > 0:
                opportunities.append(f"Optimize {keyword_performance['low_ctr_keywords']} low-CTR keywords")
            
            # Check budget utilization
            recent_performance = GoogleAdsPerformance.objects.filter(
                campaign_id=campaign_id,
                date__gte=timezone.now().date() - timezone.timedelta(days=7)
            ).aggregate(
                total_cost=Sum('cost_micros')
            )
            
            if recent_performance['total_cost'] and recent_performance['total_cost'] < 5000000:  # Less than $5
                opportunities.append("Consider increasing budget for better performance")
            
            return opportunities
            
        except Exception as e:
            logger.error(f"Optimization opportunities failed: {e}")
            return []
    
    def _select_tools(self, user_message: str, context: Dict, 
                      campaigns: List[Dict], parameters: Dict) -> List[str]:
        """Select appropriate tools based on query understanding"""
        tools = []
        
        # Keyword-related tools
        if any(word in user_message.lower() for word in ['keyword', 'keywords', 'suggest', 'generate']):
            tools.append('keyword_intelligence')
        
        # Campaign analysis tools
        if any(word in user_message.lower() for word in ['analyze', 'performance', 'metrics', 'roas', 'ctr']):
            tools.append('campaign_analysis')
        
        # Campaign discovery tools
        if campaigns:
            tools.append('campaign_discovery')
        
        # Business context tools
        if context.get('business_category') or context.get('target_audience'):
            tools.append('business_context')
        
        return tools
    
    def _calculate_confidence(self, context: Dict, campaigns: List[Dict], parameters: Dict) -> float:
        """Calculate confidence score for query understanding"""
        confidence = 0.0
        
        # Context confidence
        if context.get('business_entities'):
            confidence += 20
        if context.get('business_category'):
            confidence += 15
        if context.get('target_audience'):
            confidence += 15
        
        # Campaign discovery confidence
        if campaigns:
            confidence += 25
            # Higher confidence for exact matches
            exact_matches = [c for c in campaigns if c['match_type'] == 'exact']
            if exact_matches:
                confidence += 10
        
        # Parameter confidence
        if parameters.get('campaign_status'):
            confidence += 10
        if parameters.get('time_period'):
            confidence += 5
        
        return min(confidence, 100.0)
    
    def _handle_pipeline_error(self, user_message: str, error: str) -> Dict[str, Any]:
        """Handle pipeline errors gracefully"""
        try:
            # Use OpenAI service as fallback
            fallback_response = self.openai_service.generate_analysis_response(
                action="query_understanding_fallback",
                data={"user_message": user_message, "error": error},
                user_context="Query understanding failed, providing fallback response"
            )
            
            return {
                'success': False,
                'error': f"Query understanding failed: {error}",
                'fallback_response': fallback_response,
                'query_understanding': {
                    'stage': 'failed',
                    'confidence': 0.0,
                    'error': error
                }
            }
            
        except Exception as fallback_error:
            logger.error(f"Fallback response failed: {fallback_error}")
            return {
                'success': False,
                'error': f"Query understanding failed: {error}. Fallback also failed: {fallback_error}",
                'query_understanding': {
                    'stage': 'failed',
                    'confidence': 0.0,
                    'error': error
                }
            }

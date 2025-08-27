import logging
import sys
from typing import Dict, List, Optional, Any, Iterator
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings
import os

try:
    from google.ads.googleads.client import GoogleAdsClient
    from google.ads.googleads.errors import GoogleAdsException
    GOOGLE_ADS_AVAILABLE = True
except ImportError:
    GOOGLE_ADS_AVAILABLE = False
    logging.warning("Google Ads library not available. Install with: pip install google-ads")
    # Create a mock GoogleAdsException for when the library is not available
    class GoogleAdsException(Exception):
        pass

logger = logging.getLogger(__name__)


class GoogleAdsAPIService:
    """Service for interacting with Google Ads API v28.0.0"""
    
    def __init__(self, user_id: int = None, customer_id: str = None):
        self.user_id = user_id
        self.customer_id = customer_id
        self.client = None
        self.logger = logging.getLogger(__name__)
        
        # Set up logging for Google Ads library
        if GOOGLE_ADS_AVAILABLE:
            ga_logger = logging.getLogger('google.ads.googleads.client')
            ga_logger.addHandler(logging.StreamHandler(sys.stdout))
            ga_logger.setLevel(logging.INFO)
    
    def _get_credentials_from_db(self) -> Dict[str, Any]:
        """Get Google Ads credentials from database for the current user"""
        try:
            from accounts.models import UserGoogleAuth
            
            if not self.user_id:
                raise ValueError("User ID is required to get credentials from database")
            
            # Get the user's Google OAuth credentials
            user_auth = UserGoogleAuth.objects.filter(
                user_id=self.user_id,
                is_active=True
            ).first()
            
            if not user_auth:
                raise ValueError(f"No active Google OAuth credentials found for user {self.user_id}")
            
            # Check if token needs refresh
            if user_auth.needs_refresh():
                self.logger.info("Token needs refresh, refreshing...")
                # You can implement token refresh here or let the calling code handle it
                pass
            
            # Return credentials in the format expected by Google Ads client
            return {
                'client_id': os.getenv('GOOGLE_OAUTH_CLIENT_ID'),
                'client_secret': os.getenv('GOOGLE_OAUTH_CLIENT_SECRET'),
                'developer_token': os.getenv('GOOGLE_ADS_DEVELOPER_TOKEN'),
                'refresh_token': user_auth.refresh_token,
                'login_customer_id': self.customer_id or user_auth.google_ads_customer_id,
            }
            
        except Exception as e:
            self.logger.error(f"Error getting credentials from database: {e}")
            raise
    
    def initialize_client(self) -> bool:
        """Initialize the Google Ads client using database credentials"""
        try:
            if not GOOGLE_ADS_AVAILABLE:
                self.logger.error("Google Ads library not available")
                return False
            
            # Get credentials from database
            credentials = self._get_credentials_from_db()
            
            # Create client from credentials dictionary
            self.client = GoogleAdsClient.load_from_dict(credentials)
            self.logger.info("Google Ads client initialized successfully from database credentials")
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing Google Ads client: {e}")
            return False
    
    def get_campaigns(self, customer_id: str) -> List[Dict[str, Any]]:
        """Retrieve campaigns from Google Ads account"""
        try:
            if not self.client:
                if not self.initialize_client():
                    return []
            
            # Get the Google Ads service
            ga_service = self.client.get_service("GoogleAdsService")
            
            query = """
                SELECT
                    campaign.id,
                    campaign.name,
                    campaign.status,
                    campaign.advertising_channel_type,
                    campaign.start_date,
                    campaign.end_date,
                    campaign.budget_amount_micros,
                    campaign.budget_type
                FROM campaign
                WHERE campaign.status != 'REMOVED'
                ORDER BY campaign.id
            """
            
            campaigns = []
            stream = ga_service.search_stream(customer_id=customer_id, query=query)
            
            for batch in stream:
                rows = batch.results
                for row in rows:
                    campaign_data = {
                        'campaign_id': str(row.campaign.id),
                        'campaign_name': row.campaign.name,
                        'campaign_status': row.campaign.status.name,
                        'campaign_type': row.campaign.advertising_channel_type.name,
                        'start_date': row.campaign.start_date,
                        'end_date': row.campaign.end_date,
                        'budget_amount': row.campaign.budget_amount_micros / 1000000 if row.campaign.budget_amount_micros else None,
                        'budget_type': row.campaign.budget_type.name if row.campaign.budget_type else None,
                    }
                    campaigns.append(campaign_data)
            
            self.logger.info(f"Retrieved {len(campaigns)} campaigns for customer {customer_id}")
            return campaigns
            
        except GoogleAdsException as e:
            self.logger.error(f"Google Ads API error: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Error retrieving campaigns: {e}")
            return []
    
    def get_ad_groups(self, customer_id: str, campaign_id: str = None) -> List[Dict[str, Any]]:
        """Retrieve ad groups from Google Ads account"""
        try:
            if not self.client:
                if not self.initialize_client():
                    return []
            
            # Get the Google Ads service
            ga_service = self.client.get_service("GoogleAdsService")
            
            if campaign_id:
                query = f"""
                    SELECT
                    ad_group.id,
                    ad_group.name,
                    ad_group.status,
                    ad_group.type,
                    campaign.id
                    FROM ad_group
                    WHERE ad_group.status != 'REMOVED' AND campaign.id = {campaign_id}
                    ORDER BY ad_group.id
                """
            else:
                query = """
                    SELECT
                    ad_group.id,
                    ad_group.name,
                    ad_group.status,
                    ad_group.type,
                    campaign.id
                    FROM ad_group
                    WHERE ad_group.status != 'REMOVED'
                    ORDER BY ad_group.id
                """
            
            ad_groups = []
            stream = ga_service.search_stream(customer_id=customer_id, query=query)
            
            for batch in stream:
                rows = batch.results
                for row in rows:
                    ad_group_data = {
                        'ad_group_id': str(row.ad_group.id),
                        'ad_group_name': row.ad_group.name,
                        'status': row.ad_group.status.name,
                        'type': row.ad_group.type.name,
                        'campaign_id': str(row.campaign.id),
                    }
                    ad_groups.append(ad_group_data)
            
            self.logger.info(f"Retrieved {len(ad_groups)} ad groups for customer {customer_id}")
            return ad_groups
            
        except GoogleAdsException as e:
            self.logger.error(f"Google Ads API error: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Error retrieving ad groups: {e}")
            return []
    
    def get_keywords(self, customer_id: str, ad_group_id: str = None) -> List[Dict[str, Any]]:
        """Retrieve keywords from Google Ads account"""
        try:
            if not self.client:
                if not self.initialize_client():
                    return []
            
            # Get the Google Ads service
            ga_service = self.client.get_service("GoogleAdsService")
            
            if ad_group_id:
                query = f"""
                    SELECT
                    ad_group_criterion.criterion_id,
                    ad_group_criterion.keyword.text,
                    ad_group_criterion.keyword.match_type,
                    ad_group_criterion.status,
                    ad_group_criterion.quality_info.quality_score,
                    ad_group.id
                    FROM ad_group_criterion
                    WHERE ad_group_criterion.type = 'KEYWORD' 
                        AND ad_group_criterion.status != 'REMOVED'
                        AND ad_group.id = {ad_group_id}
                    ORDER BY ad_group_criterion.criterion_id
                """
            else:
                query = """
                    SELECT
                    ad_group_criterion.criterion_id,
                    ad_group_criterion.keyword.text,
                    ad_group_criterion.keyword.match_type,
                    ad_group_criterion.status,
                    ad_group_criterion.quality_info.quality_score,
                    ad_group.id
                    FROM ad_group_criterion
                    WHERE ad_group_criterion.type = 'KEYWORD' 
                        AND ad_group_criterion.status != 'REMOVED'
                    ORDER BY ad_group_criterion.criterion_id
                """
            
            keywords = []
            stream = ga_service.search_stream(customer_id=customer_id, query=query)
            
            for batch in stream:
                rows = batch.results
                for row in rows:
                    keyword_data = {
                        'keyword_id': str(row.ad_group_criterion.criterion_id),
                        'keyword_text': row.ad_group_criterion.keyword.text,
                        'match_type': row.ad_group_criterion.keyword.match_type.name,
                        'status': row.ad_group_criterion.status.name,
                        'quality_score': row.ad_group_criterion.quality_info.quality_score if row.ad_group_criterion.quality_info.quality_score else None,
                        'ad_group_id': str(row.ad_group.id),
                    }
                    keywords.append(keyword_data)
            
            self.logger.info(f"Retrieved {len(keywords)} keywords for customer {customer_id}")
            return keywords
            
        except GoogleAdsException as e:
            self.logger.error(f"Google Ads API error: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Error retrieving keywords: {e}")
            return []
    
    def get_performance_data(self, customer_id: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Retrieve performance data from Google Ads account"""
        try:
            if not self.client:
                if not self.initialize_client():
                    return []
            
            # Get the Google Ads service
            ga_service = self.client.get_service("GoogleAdsService")
            
            query = f"""
                SELECT
                campaign.id,
                campaign.name,
                ad_group.id,
                ad_group.name,
                ad_group_criterion.criterion_id,
                ad_group_criterion.keyword.text,
                metrics.impressions,
                metrics.clicks,
                metrics.cost_micros,
                metrics.conversions,
                metrics.conversions_value,
                segments.date
                FROM keyword_view
                WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
                ORDER BY segments.date DESC
            """
            
            performance_data = []
            stream = ga_service.search_stream(customer_id=customer_id, query=query)
            
            for batch in stream:
                rows = batch.results
                for row in rows:
                    data = {
                        'campaign_id': str(row.campaign.id) if row.campaign.id else None,
                        'campaign_name': row.campaign.name if row.campaign.name else None,
                        'ad_group_id': str(row.ad_group.id) if row.ad_group.id else None,
                        'ad_group_name': row.ad_group.name if row.ad_group.name else None,
                        'keyword_id': str(row.ad_group_criterion.criterion_id) if row.ad_group_criterion.criterion_id else None,
                        'keyword_text': row.ad_group_criterion.keyword.text if row.ad_group_criterion.keyword.text else None,
                        'impressions': row.metrics.impressions,
                        'clicks': row.metrics.clicks,
                        'cost_micros': row.metrics.cost_micros,
                        'conversions': row.metrics.conversions,
                        'conversion_value': row.metrics.conversions_value,
                        'date': row.segments.date,
                    }
                    performance_data.append(data)
            
            self.logger.info(f"Retrieved {len(performance_data)} performance records for customer {customer_id}")
            return performance_data
            
        except GoogleAdsException as e:
            self.logger.error(f"Google Ads API error: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Error retrieving performance data: {e}")
            return []
    
    def test_connection(self, customer_id: str) -> Dict[str, Any]:
        """Test the connection to Google Ads API"""
        try:
            if not self.client:
                if not self.initialize_client():
                    return {'success': False, 'error': 'Failed to initialize client'}
            
            # Get the Google Ads service
            ga_service = self.client.get_service("GoogleAdsService")
            
            # Try to get a simple query
            query = "SELECT customer.id FROM customer LIMIT 1"
            
            stream = ga_service.search_stream(customer_id=customer_id, query=query)
            
            # Just check if we can make the call
            for batch in stream:
                if batch.results:
                    return {
                        'success': True,
                        'message': 'Connection successful',
                        'customer_id': customer_id
                    }
            
            return {
                'success': True,
                'message': 'Connection successful (no results)',
                'customer_id': customer_id
            }
            
        except GoogleAdsException as e:
            return {
                'success': False,
                'error': f'Google Ads API error: {e}',
                'customer_id': customer_id
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Connection error: {e}',
                'customer_id': customer_id
            }

    def request_account_access(self, manager_customer_id: str, client_customer_id: str) -> Dict[str, Any]:
        """Request access to another Google Ads account using CustomerClientLinkService v28.0.0"""
        try:
            if not self.client:
                if not self.initialize_client():
                    return {'success': False, 'error': 'Failed to initialize client'}
            
            # Validate that we're not trying to request access to ourselves
            if manager_customer_id == client_customer_id:
                return {
                    'success': False, 
                    'error': 'Manager and client customer IDs cannot be the same'
                }
            
            # Use the latest Google Ads API v28.0.0 approach
            customer_client_link_service = self.client.get_service("CustomerClientLinkService")
            customer_client_link_operation = self.client.get_type("CustomerClientLinkOperation")
            
            # Create the link object
            link = customer_client_link_operation.create
            link.client_customer = f"customers/{client_customer_id}"
            link.status = self.client.get_type("ManagerLinkStatusEnum").ManagerLinkStatus.PENDING
            
            try:
                # Make the API call to request access
                response = customer_client_link_service.mutate_customer_client_link(
                    customer_id=manager_customer_id,
                    operation=customer_client_link_operation
                )
                
                self.logger.info(f"Link request sent with resource name: {response.result.resource_name}")
                
                return {
                    'success': True,
                    'message': 'Link request sent successfully',
                    'resource_name': response.result.resource_name,
                    'manager_customer_id': manager_customer_id,
                    'client_customer_id': client_customer_id
                }
                
            except GoogleAdsException as ex:
                self.logger.error(f"Request failed: {ex.failure}")
                
                # Check for specific permission errors
                if "USER_PERMISSION_DENIED" in str(ex):
                    return {
                        'success': False,
                        'error': f'Permission denied. Make sure:\n'
                                f'1. Your login_customer_id ({self.client.login_customer_id}) is your MANAGER account (MCC)\n'
                                f'2. You have permission to manage the target account\n'
                                f'3. The target account ID is correct\n'
                                f'Original error: {ex.failure if hasattr(ex, "failure") else str(ex)}'
                    }
                
                return {
                    'success': False,
                    'error': f'Google Ads API error: {ex.failure if hasattr(ex, "failure") else str(ex)}'
                }
                
        except Exception as e:
            self.logger.error(f"Error in request_account_access: {e}")
            return {'success': False, 'error': str(e)}

    def get_pending_access_requests(self, manager_customer_id: str) -> Dict[str, Any]:
        """Get pending access requests for a manager account"""
        try:
            if not self.client:
                if not self.initialize_client():
                    return {'success': False, 'error': 'Failed to initialize client'}
            
            # Get the Google Ads service for the search
            ga_service = self.client.get_service("GoogleAdsService")
            
            # Query for pending customer client links
            query = """
                SELECT
                    customer_client_link.client_customer,
                    customer_client_link.manager_link_id,
                    customer_client_link.status,
                    customer_client_link.pending_manager_link_invitation
                FROM customer_client_link
                WHERE customer_client_link.status = 'PENDING'
            """
            
            stream = ga_service.search_stream(customer_id=manager_customer_id, query=query)
            
            pending_requests = []
            for batch in stream:
                rows = batch.results
                for row in rows:
                    request_data = {
                        'client_customer': row.customer_client_link.client_customer,
                        'manager_link_id': row.customer_client_link.manager_link_id,
                        'status': row.customer_client_link.status.name if row.customer_client_link.status else None,
                        'pending_manager_link_invitation': row.customer_client_link.pending_manager_link_invitation
                    }
                    pending_requests.append(request_data)
            
            self.logger.info(f"Retrieved {len(pending_requests)} pending access requests for manager {manager_customer_id}")
            
            return {
                'success': True,
                'pending_requests': pending_requests,
                'manager_customer_id': manager_customer_id
            }
            
        except GoogleAdsException as e:
            self.logger.error(f"Google Ads API error in get_pending_access_requests: {e}")
            return {
                'success': False,
                'error': f'Google Ads API error: {e.failure if hasattr(e, "failure") else str(e)}'
            }
        except Exception as e:
            self.logger.error(f"Error in get_pending_access_requests: {e}")
            return {'success': False, 'error': str(e)} 

def send_link_request(manager_customer_id: str, client_customer_id: str, user_id: int = None) -> Dict[str, Any]:
    """
    Standalone function to send linking request using Google Ads API v28.0.0
    This matches the user's requested code structure
    """
    try:
        # Create API service instance with user credentials
        api_service = GoogleAdsAPIService(user_id=user_id, customer_id=manager_customer_id)
        if not api_service.initialize_client():
            return {'success': False, 'error': 'Failed to initialize Google Ads client'}
        
        client = api_service.client
        
        # Get the service and operation types
        customer_client_link_service = client.get_service("CustomerClientLinkService")
        customer_client_link_operation = client.get_type("CustomerClientLinkOperation")
        
        # Create the link object
        link = customer_client_link_operation.create
        link.client_customer = f"customers/{client_customer_id}"
        link.status = client.get_type("ManagerLinkStatusEnum").ManagerLinkStatus.PENDING
        
        try:
            # Make the API call to request access
            response = customer_client_link_service.mutate_customer_client_link(
                customer_id=manager_customer_id,
                operation=customer_client_link_operation
            )
            
            print(f"Link request sent with resource name: {response.result.resource_name}")
            return {
                'success': True,
                'resource_name': response.result.resource_name,
                'message': 'Link request sent successfully'
            }
            
        except GoogleAdsException as ex:
            print(f"Request failed: {ex.failure}")
            return {
                'success': False,
                'error': f'Google Ads API error: {ex.failure}'
            }
            
    except Exception as e:
        print(f"Error: {e}")
        return {
            'success': False,
            'error': str(e)
        } 
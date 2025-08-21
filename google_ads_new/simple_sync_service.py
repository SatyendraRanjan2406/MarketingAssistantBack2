#!/usr/bin/env python3
"""
Simple Google Ads Sync Service for testing
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any
from django.utils import timezone


class SimpleGoogleAdsSyncService:
    """Simple service for testing single client sync"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def sync_single_client_account(self, client_customer_id: str, days_back: int = 7, sync_types: list = None) -> Dict[str, Any]:
        """
        Sync a single client Google Ads account (simplified version for testing)
        """
        if sync_types is None:
            sync_types = ['campaigns', 'ad_groups', 'keywords', 'performance']
        
        try:
            self.logger.info(f"Starting single client sync for account: {client_customer_id}")
            
            # Calculate date range
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days_back)
            
            self.logger.info(f"Date range: {start_date} to {end_date}")
            
            # Create a simple sync summary
            sync_summary = {
                'client_customer_id': client_customer_id,
                'account_name': f'Account {client_customer_id}',
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'sync_types': sync_types,
                'campaigns_synced': 0,
                'ad_groups_synced': 0,
                'keywords_synced': 0,
                'performance_records_synced': 0,
                'errors': []
            }
            
            self.logger.info(f"Single client sync completed for account {client_customer_id}")
            
            return {
                'success': True,
                'summary': sync_summary
            }
            
        except Exception as e:
            error_msg = f"Error in single client sync for account {client_customer_id}: {str(e)}"
            self.logger.error(error_msg)
            return {'success': False, 'error': error_msg}

"""
Simple Google Ads Sync Service for testing
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any
from django.utils import timezone


class SimpleGoogleAdsSyncService:
    """Simple service for testing single client sync"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def sync_single_client_account(self, client_customer_id: str, days_back: int = 7, sync_types: list = None) -> Dict[str, Any]:
        """
        Sync a single client Google Ads account (simplified version for testing)
        """
        if sync_types is None:
            sync_types = ['campaigns', 'ad_groups', 'keywords', 'performance']
        
        try:
            self.logger.info(f"Starting single client sync for account: {client_customer_id}")
            
            # Calculate date range
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days_back)
            
            self.logger.info(f"Date range: {start_date} to {end_date}")
            
            # Create a simple sync summary
            sync_summary = {
                'client_customer_id': client_customer_id,
                'account_name': f'Account {client_customer_id}',
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'sync_types': sync_types,
                'campaigns_synced': 0,
                'ad_groups_synced': 0,
                'keywords_synced': 0,
                'performance_records_synced': 0,
                'errors': []
            }
            
            self.logger.info(f"Single client sync completed for account {client_customer_id}")
            
            return {
                'success': True,
                'summary': sync_summary
            }
            
        except Exception as e:
            error_msg = f"Error in single client sync for account {client_customer_id}: {str(e)}"
            self.logger.error(error_msg)
            return {'success': False, 'error': error_msg}


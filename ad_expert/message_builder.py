"""
Message Builder for structured response formatting
"""

import json
import logging
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class MessageType(Enum):
    """Types of message content that can be displayed"""
    TEXT = "text"
    HEADING = "heading"
    SUBHEADING = "subheading"
    TABLE = "table"
    CHART = "chart"
    PIE_CHART = "pie_chart"
    DOTTED_LIST = "dotted_list"
    NUMBERED_LIST = "numbered_list"
    BULLET_LIST = "bullet_list"
    CARD = "card"
    ALERT = "alert"
    BUTTON = "button"
    DIVIDER = "divider"

@dataclass
class MessageContent:
    """Individual message content item"""
    type: MessageType
    content: Any
    order: int
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class MessageTemplate:
    """Complete message template with ordered content"""
    content_items: List[MessageContent]
    message_type: str = "response"  # response, error, info, warning, success
    title: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class MessageBuilder:
    """Builder for creating structured messages"""
    
    def __init__(self):
        self.content_items = []
        self.current_order = 0
    
    def add_text(self, text: str, order: Optional[int] = None) -> 'MessageBuilder':
        """Add text content"""
        self._add_content(MessageType.TEXT, text, order)
        return self
    
    def add_heading(self, text: str, level: int = 1, order: Optional[int] = None) -> 'MessageBuilder':
        """Add heading content"""
        self._add_content(MessageType.HEADING, text, order, {"level": level})
        return self
    
    def add_subheading(self, text: str, order: Optional[int] = None) -> 'MessageBuilder':
        """Add subheading content"""
        self._add_content(MessageType.SUBHEADING, text, order)
        return self
    
    def add_table(self, data: List[Dict[str, Any]], headers: Optional[List[str]] = None, 
                  order: Optional[int] = None, **kwargs) -> 'MessageBuilder':
        """Add table content"""
        table_data = {
            "headers": headers or [],
            "rows": data,
            **kwargs
        }
        self._add_content(MessageType.TABLE, table_data, order)
        return self
    
    def add_chart(self, chart_type: str, data: Dict[str, Any], 
                  order: Optional[int] = None, **kwargs) -> 'MessageBuilder':
        """Add chart content"""
        chart_data = {
            "type": chart_type,
            "data": data,
            **kwargs
        }
        self._add_content(MessageType.CHART, chart_data, order)
        return self
    
    def add_pie_chart(self, data: List[Dict[str, Any]], 
                      order: Optional[int] = None, **kwargs) -> 'MessageBuilder':
        """Add pie chart content"""
        pie_data = {
            "data": data,
            **kwargs
        }
        self._add_content(MessageType.PIE_CHART, pie_data, order)
        return self
    
    def add_dotted_list(self, items: List[str], order: Optional[int] = None) -> 'MessageBuilder':
        """Add dotted list content"""
        self._add_content(MessageType.DOTTED_LIST, items, order)
        return self
    
    def add_numbered_list(self, items: List[str], order: Optional[int] = None) -> 'MessageBuilder':
        """Add numbered list content"""
        self._add_content(MessageType.NUMBERED_LIST, items, order)
        return self
    
    def add_bullet_list(self, items: List[str], order: Optional[int] = None) -> 'MessageBuilder':
        """Add bullet list content"""
        self._add_content(MessageType.BULLET_LIST, items, order)
        return self
    
    def add_card(self, title: str, content: str, order: Optional[int] = None, **kwargs) -> 'MessageBuilder':
        """Add card content"""
        card_data = {
            "title": title,
            "content": content,
            **kwargs
        }
        self._add_content(MessageType.CARD, card_data, order)
        return self
    
    def add_alert(self, message: str, alert_type: str = "info", order: Optional[int] = None) -> 'MessageBuilder':
        """Add alert content"""
        alert_data = {
            "message": message,
            "type": alert_type  # info, success, warning, error
        }
        self._add_content(MessageType.ALERT, alert_data, order)
        return self
    
    def add_button(self, text: str, action: str, order: Optional[int] = None, **kwargs) -> 'MessageBuilder':
        """Add button content"""
        button_data = {
            "text": text,
            "action": action,
            **kwargs
        }
        self._add_content(MessageType.BUTTON, button_data, order)
        return self
    
    def add_divider(self, order: Optional[int] = None) -> 'MessageBuilder':
        """Add divider content"""
        self._add_content(MessageType.DIVIDER, None, order)
        return self
    
    def _add_content(self, content_type: MessageType, content: Any, 
                    order: Optional[int] = None, metadata: Optional[Dict[str, Any]] = None):
        """Add content item with order"""
        if order is None:
            order = self.current_order
            self.current_order += 1
        
        message_content = MessageContent(
            type=content_type,
            content=content,
            order=order,
            metadata=metadata
        )
        self.content_items.append(message_content)
    
    def build(self, message_type: str = "response", title: Optional[str] = None, 
              metadata: Optional[Dict[str, Any]] = None) -> MessageTemplate:
        """Build the final message template"""
        # Sort content items by order
        sorted_items = sorted(self.content_items, key=lambda x: x.order)
        
        return MessageTemplate(
            content_items=sorted_items,
            message_type=message_type,
            title=title,
            metadata=metadata
        )
    
    def to_dict(self, message_type: str = "response", title: Optional[str] = None, 
                metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Convert to dictionary format for API response"""
        template = self.build(message_type, title, metadata)
        
        return {
            "message_type": template.message_type,
            "title": template.title,
            "content": [
                {
                    "type": item.type.value,
                    "content": item.content,
                    "order": item.order,
                    "metadata": item.metadata or {}
                }
                for item in template.content_items
            ],
            "metadata": template.metadata or {}
        }

class CustomerSelectionMessageBuilder:
    """Specialized builder for customer selection messages"""
    
    @staticmethod
    def build_no_accounts_message() -> Dict[str, Any]:
        """Build message when no Google Ads accounts are found"""
        builder = MessageBuilder()
        builder.add_alert(
            "No Google Ads accounts found. Please connect your Google Ads account first.",
            alert_type="warning",
            order=1
        )
        builder.add_text(
            "To get started, please connect your Google Ads account through the settings page.",
            order=2
        )
        return builder.to_dict(message_type="info", title="Account Setup Required")
    
    @staticmethod
    def build_single_account_message(customer_id: str) -> Dict[str, Any]:
        """Build message when only one account is found"""
        builder = MessageBuilder()
        builder.add_alert(
            f"I found 1 Google Ads account: {customer_id}. I'll use this account for your queries.",
            alert_type="success",
            order=1
        )
        builder.add_text(
            "You can now ask me about your campaigns, keywords, and performance data.",
            order=2
        )
        return builder.to_dict(message_type="success", title="Account Selected")
    
    @staticmethod
    def build_multiple_accounts_message(accessible_customers: List[str]) -> Dict[str, Any]:
        """Build message when multiple accounts are found"""
        builder = MessageBuilder()
        builder.add_heading(f"Select Google Ads Account", level=2, order=1)
        builder.add_text(
            f"I found {len(accessible_customers)} Google Ads accounts:",
            order=2
        )
        
        # Create numbered list of accounts
        account_items = []
        for i, customer_id in enumerate(accessible_customers, 1):
            account_items.append(f"{i}. {customer_id}")
        
        builder.add_numbered_list(account_items, order=3)
        builder.add_text(
            "Please select which account you'd like to use by replying with the account number or the full customer ID.",
            order=4
        )
        
        return builder.to_dict(message_type="info", title="Account Selection Required")
    
    @staticmethod
    def build_selection_confirmation_message(customer_id: str) -> Dict[str, Any]:
        """Build message when customer selection is confirmed"""
        builder = MessageBuilder()
        builder.add_alert(
            f"Great! I've selected Google Ads account {customer_id} for this conversation.",
            alert_type="success",
            order=1
        )
        builder.add_text(
            "You can now ask me about your campaigns, keywords, and performance data.",
            order=2
        )
        return builder.to_dict(message_type="success", title="Account Selected")

class IntentMappingMessageBuilder:
    """Specialized builder for intent mapping messages"""
    
    @staticmethod
    def build_intent_mapping_message(intent_result: Dict[str, Any]) -> Dict[str, Any]:
        """Build message for intent mapping results"""
        builder = MessageBuilder()
        
        # Add heading
        builder.add_heading("Query Analysis", level=2, order=1)
        
        # Add confidence and reasoning
        confidence = intent_result.get('confidence', 0)
        reasoning = intent_result.get('reasoning', '')
        
        if confidence > 0.8:
            builder.add_alert(f"High confidence analysis ({confidence:.1%})", alert_type="success", order=2)
        elif confidence > 0.5:
            builder.add_alert(f"Medium confidence analysis ({confidence:.1%})", alert_type="warning", order=2)
        else:
            builder.add_alert(f"Low confidence analysis ({confidence:.1%})", alert_type="warning", order=2)
        
        # Add reasoning
        if reasoning:
            builder.add_text(f"Analysis: {reasoning}", order=3)
        
        # Add action groups
        action_groups = intent_result.get('action_groups', [])
        if action_groups:
            builder.add_subheading("Recommended Actions", order=4)
            
            for i, group in enumerate(action_groups, 1):
                actions = group.get('actions', [])
                date_ranges = group.get('date_ranges', [])
                filters = group.get('filters', [])
                
                # Create card for each action group
                card_content = f"Actions: {', '.join(actions)}"
                if date_ranges:
                    card_content += f"\nDate Ranges: {', '.join(date_ranges)}"
                if filters:
                    filter_text = ', '.join([f"{k}: {v}" for f in filters for k, v in f.items()])
                    card_content += f"\nFilters: {filter_text}"
                
                builder.add_card(
                    title=f"Action Group {i}",
                    content=card_content,
                    order=4 + i
                )
        
        return builder.to_dict(message_type="response", title="Query Analysis Complete")

class DataDisplayMessageBuilder:
    """Specialized builder for data display messages"""
    
    @staticmethod
    def build_campaigns_table(campaigns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build campaigns data table"""
        builder = MessageBuilder()
        
        if not campaigns:
            builder.add_alert("No campaigns found matching your criteria.", alert_type="info", order=1)
            return builder.to_dict(message_type="info", title="Campaigns")
        
        # Prepare table data
        table_data = []
        for campaign in campaigns:
            table_data.append({
                "ID": campaign.get('id', ''),
                "Name": campaign.get('name', ''),
                "Status": campaign.get('status', ''),
                "Type": campaign.get('advertising_channel_type', ''),
                "Impressions": campaign.get('impressions', 0),
                "Clicks": campaign.get('clicks', 0),
                "CTR": f"{campaign.get('ctr', 0):.2f}%",
                "Cost": f"${campaign.get('cost', 0):.2f}"
            })
        
        builder.add_heading(f"Campaigns ({len(campaigns)} found)", level=2, order=1)
        builder.add_table(
            data=table_data,
            headers=["ID", "Name", "Status", "Type", "Impressions", "Clicks", "CTR", "Cost"],
            order=2
        )
        
        return builder.to_dict(message_type="response", title="Campaigns Data")
    
    @staticmethod
    def build_performance_chart(performance_data: List[Dict[str, Any]], chart_type: str = "line") -> Dict[str, Any]:
        """Build performance chart"""
        builder = MessageBuilder()
        
        builder.add_heading("Performance Overview", level=2, order=1)
        builder.add_chart(
            chart_type=chart_type,
            data={
                "labels": [item.get('date', '') for item in performance_data],
                "datasets": [
                    {
                        "label": "Impressions",
                        "data": [item.get('impressions', 0) for item in performance_data]
                    },
                    {
                        "label": "Clicks", 
                        "data": [item.get('clicks', 0) for item in performance_data]
                    }
                ]
            },
            order=2
        )
        
        return builder.to_dict(message_type="response", title="Performance Chart")

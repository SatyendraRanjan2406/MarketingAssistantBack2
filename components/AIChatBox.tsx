import React, { useState, useEffect, useRef } from 'react';
import CampaignFormBlock from './ChatBlocks/CampaignFormBlock';
import AnalysisBlock from './ChatBlocks/AnalysisBlock';

interface AIChatBoxProps {
  token: string;
  className?: string;
}

interface UIBlock {
  type: string;
  [key: string]: any;
}

interface ChatResponse {
  success: boolean;
  session_id: string;
  response: {
    blocks: UIBlock[];
    session_id: string | null;
    metadata: any | null;
  };
  intent: {
    action: string;
    confidence: number;
    parameters: Record<string, any>;
    requires_auth: boolean;
  };
}

const AIChatBox: React.FC<AIChatBoxProps> = ({ token, className = '' }) => {
  const [messages, setMessages] = useState<any[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [sessions, setSessions] = useState<any[]>([]);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadSessions();
    createNewSession();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadSessions = async () => {
    try {
      const response = await fetch('http://localhost:8000/google-ads-new/api/chat/sessions/', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      const result = await response.json();
      if (result.success) {
        setSessions(result.sessions);
      }
    } catch (error) {
      console.error('Failed to load sessions:', error);
    }
  };

  const createNewSession = async () => {
    try {
      const response = await fetch('http://localhost:8000/google-ads-new/api/chat/sessions/create/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ title: 'New Chat Session' }),
      });
      const result = await response.json();
      if (result.success) {
        setCurrentSessionId(result.session_id);
        localStorage.setItem('currentSessionId', result.session_id);
      }
    } catch (error) {
      console.error('Failed to create session:', error);
    }
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || !currentSessionId) return;

    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/google-ads-new/api/chat/message/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          message: inputMessage,
          session_id: currentSessionId,
        }),
      });

      const result: ChatResponse = await response.json();
      
      if (result.success) {
        const aiMessage = {
          id: Date.now() + 1,
          role: 'assistant',
          response: result.response,
          intent: result.intent,
          timestamp: new Date().toISOString(),
        };
        setMessages(prev => [...prev, aiMessage]);
      } else {
        const errorMessage = {
          id: Date.now() + 1,
          role: 'assistant',
          content: `Error: ${result.response?.blocks?.[0]?.content || 'Unknown error'}`,
          timestamp: new Date().toISOString(),
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      const errorMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: 'Failed to send message. Please try again.',
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCampaignFormSubmit = async (campaignData: any) => {
    if (!currentSessionId) return;

    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/google-ads-new/api/chat/message/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          message: `Create campaign with name: ${campaignData.name}, budget: $${campaignData.budget_amount_micros}, type: ${campaignData.channel_type}, status: ${campaignData.status}`,
          session_id: currentSessionId,
          campaign_data: campaignData
        }),
      });

      const result: ChatResponse = await response.json();
      
      if (result.success) {
        const aiMessage = {
          id: Date.now() + 1,
          role: 'assistant',
          response: result.response,
          intent: result.intent,
          timestamp: new Date().toISOString(),
        };
        setMessages(prev => [...prev, aiMessage]);
      } else {
        const errorMessage = {
          id: Date.now() + 1,
          role: 'assistant',
          content: `Error: ${result.response?.blocks?.[0]?.content || 'Failed to create campaign'}`,
          timestamp: new Date().toISOString(),
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    } catch (error) {
      console.error('Failed to create campaign:', error);
      const errorMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: 'Failed to create campaign. Please try again.',
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const renderMessage = (message: any) => {
    if (message.role === 'user') {
      return (
        <div className="flex justify-end mb-4">
          <div className="bg-blue-500 text-white rounded-lg px-4 py-2 max-w-xs lg:max-w-md">
            {message.content}
          </div>
        </div>
      );
    }

    if (message.role === 'assistant') {
      return (
        <div className="flex justify-start mb-4">
          <div className="bg-gray-100 rounded-lg px-4 py-2 max-w-xs lg:max-w-md">
            {message.response?.blocks ? (
              <div className="space-y-3">
                {message.response.blocks.map((block: UIBlock, index: number) => (
                  <div key={index}>
                    {renderBlock(block)}
                  </div>
                ))}
              </div>
            ) : (
              <div>{message.content}</div>
            )}
          </div>
        </div>
      );
    }

    return null;
  };

  const renderBlock = (block: UIBlock) => {
    switch (block.type) {
      case 'text':
        return (
          <div className={`text-gray-700 ${
            block.style === 'heading' ? 'text-xl font-bold' : 
            block.style === 'highlight' ? 'bg-yellow-100 p-2 rounded border-l-4 border-yellow-400' : 
            'leading-relaxed'
          }`}>
            {block.content}
          </div>
        );
        
      case 'campaign_form':
        return (
          <CampaignFormBlock
            title={block.title}
            description={block.description}
            fields={block.fields}
            onSubmit={handleCampaignFormSubmit}
          />
        );
        
      case 'actions':
        return (
          <div className="bg-white rounded-lg border p-4">
            {block.title && (
              <h3 className="font-semibold text-gray-800 mb-3">{block.title}</h3>
            )}
            <div className="flex flex-wrap gap-2">
              {block.items && block.items.map((item: any, index: number) => {
                // Generate different colors for different action types
                const getButtonColor = (actionId: string) => {
                  if (actionId.includes('create') || actionId.includes('add')) {
                    return 'bg-green-500 hover:bg-green-600';
                  } else if (actionId.includes('edit') || actionId.includes('update')) {
                    return 'bg-blue-500 hover:bg-blue-600';
                  } else if (actionId.includes('delete') || actionId.includes('remove')) {
                    return 'bg-red-500 hover:bg-red-600';
                  } else if (actionId.includes('pause') || actionId.includes('stop')) {
                    return 'bg-yellow-500 hover:bg-yellow-600';
                  } else if (actionId.includes('resume') || actionId.includes('start')) {
                    return 'bg-emerald-500 hover:bg-emerald-600';
                  } else if (actionId.includes('view') || actionId.includes('get') || actionId.includes('show')) {
                    return 'bg-indigo-500 hover:bg-indigo-600';
                  } else if (actionId.includes('optimize') || actionId.includes('improve')) {
                    return 'bg-purple-500 hover:bg-purple-600';
                  } else if (actionId.includes('analyze') || actionId.includes('check')) {
                    return 'bg-teal-500 hover:bg-teal-600';
                  } else if (actionId.includes('generate') || actionId.includes('create')) {
                    return 'bg-pink-500 hover:bg-pink-600';
                  } else {
                    return 'bg-gray-500 hover:bg-gray-600';
                  }
                };

                return (
                  <button
                    key={index}
                    onClick={() => handleActionClick(item.id, item.label)}
                    className={`text-white px-4 py-2 rounded-lg transition-colors font-medium ${getButtonColor(item.id)}`}
                  >
                    {item.label || item.id}
                  </button>
                );
              })}
            </div>
          </div>
        );
        
      // Analysis blocks
      case 'audience_analysis':
        return (
          <AnalysisBlock
            type="audience_analysis"
            title="Audience Analysis"
            data={block}
            account={block.account}
            timestamp={block.timestamp}
          />
        );
        
      case 'creative_fatigue_analysis':
        return (
          <AnalysisBlock
            type="creative_fatigue_analysis"
            title="Creative Fatigue Analysis"
            data={block}
            account={block.account}
            timestamp={block.timestamp}
          />
        );
        
      case 'video_performance_analysis':
        return (
          <AnalysisBlock
            type="video_performance_analysis"
            title="Video Performance Analysis"
            data={block}
            account={block.account}
            timestamp={block.timestamp}
          />
        );
        
      case 'performance_comparison':
        return (
          <AnalysisBlock
            type="performance_comparison"
            title="Performance Comparison"
            data={block}
            account={block.account}
            timestamp={block.timestamp}
          />
        );
        
      case 'campaign_optimizations':
        return (
          <AnalysisBlock
            type="campaign_optimizations"
            title="Campaign Optimization Recommendations"
            data={block}
            account={block.account}
            timestamp={block.timestamp}
          />
        );
        
      case 'adset_optimizations':
        return (
          <AnalysisBlock
            type="adset_optimizations"
            title="Ad Set Optimization Recommendations"
            data={block}
            account={block.account}
            timestamp={block.timestamp}
          />
        );
        
      case 'ad_optimizations':
        return (
          <AnalysisBlock
            type="ad_optimizations"
            title="Ad Optimization Recommendations"
            data={block}
            account={block.account}
            timestamp={block.timestamp}
          />
        );
        
      case 'placement_analysis':
        return (
          <AnalysisBlock
            type="placement_analysis"
            title="Placement Performance Analysis"
            data={block}
            account={block.account}
            timestamp={block.timestamp}
          />
        );
        
      case 'device_performance_analysis':
        return (
          <AnalysisBlock
            type="device_performance_analysis"
            title="Device Performance Analysis"
            data={block}
            account={block.account}
            timestamp={block.timestamp}
          />
        );
        
      case 'time_performance_analysis':
        return (
          <AnalysisBlock
            type="time_performance_analysis"
            title="Time-based Performance Analysis"
            data={block}
            account={block.account}
            timestamp={block.timestamp}
          />
        );
        
      case 'demographic_analysis':
        return (
          <AnalysisBlock
            type="demographic_analysis"
            title="Demographic Performance Analysis"
            data={block}
            account={block.account}
            timestamp={block.timestamp}
          />
        );
        
      case 'competitor_analysis':
        return (
          <AnalysisBlock
            type="competitor_analysis"
            title="Competitor Analysis"
            data={block}
            account={block.account}
            timestamp={block.timestamp}
          />
        );
        
      case 'creative_testing':
        return (
          <AnalysisBlock
            type="creative_testing"
            title="Creative Testing Recommendations"
            data={block}
            account={block.account}
            timestamp={block.timestamp}
          />
        );
        
      case 'technical_compliance':
        return (
          <AnalysisBlock
            type="technical_compliance"
            title="Technical Compliance Check"
            data={block}
            account={block.account}
            timestamp={block.timestamp}
          />
        );
        
      case 'audience_insights':
        return (
          <AnalysisBlock
            type="audience_insights"
            title="Audience Insights"
            data={block}
            account={block.account}
            timestamp={block.timestamp}
          />
        );
        
              case 'budget_optimizations':
          return (
            <AnalysisBlock
              type="budget_optimizations"
              title="Budget Optimization Recommendations"
              data={block}
              account={block.account}
              timestamp={block.timestamp}
            />
          );
        
        // Additional Google Ads analysis blocks
        case 'campaign_consistency_analysis':
          return (
            <AnalysisBlock
              type="campaign_consistency_analysis"
              title="Campaign Consistency Analysis"
              data={block}
              account={block.account}
              timestamp={block.timestamp}
            />
          );
        
        case 'sitelink_analysis':
          return (
            <AnalysisBlock
              type="sitelink_analysis"
              title="Sitelink Analysis"
              data={block}
              account={block.account}
              timestamp={block.timestamp}
            />
          );
        
        case 'landing_page_analysis':
          return (
            <AnalysisBlock
              type="landing_page_analysis"
              title="Landing Page Analysis"
              data={block}
              account={block.account}
              timestamp={block.timestamp}
            />
          );
        
        case 'duplicate_keyword_analysis':
          return (
            <AnalysisBlock
              type="duplicate_keyword_analysis"
              title="Duplicate Keyword Analysis"
              data={block}
              account={block.account}
              timestamp={block.timestamp}
            />
          );
        
        case 'keyword_trends_analysis':
          return (
            <AnalysisBlock
              type="keyword_trends_analysis"
              title="Keyword Trends Analysis"
              data={block}
              account={block.account}
              timestamp={block.timestamp}
            />
          );
        
        case 'auction_insights_analysis':
          return (
            <AnalysisBlock
              type="auction_insights_analysis"
              title="Auction Insights Analysis"
              data={block}
              account={block.account}
              timestamp={block.timestamp}
            />
          );
        
        case 'search_term_analysis':
          return (
            <AnalysisBlock
              type="search_term_analysis"
              title="Search Term Analysis"
              data={block}
              account={block.account}
              timestamp={block.timestamp}
            />
          );
        
        case 'ads_showing_time_analysis':
          return (
            <AnalysisBlock
              type="ads_showing_time_analysis"
              title="Ads Showing Time Analysis"
              data={block}
              account={block.account}
              timestamp={block.timestamp}
            />
          );
        
        case 'device_performance_detailed_analysis':
          return (
            <AnalysisBlock
              type="device_performance_detailed_analysis"
              title="Device Performance Analysis"
              data={block}
              account={block.account}
              timestamp={block.timestamp}
            />
          );
        
        case 'location_performance_analysis':
          return (
            <AnalysisBlock
              type="location_performance_analysis"
              title="Location Performance Analysis"
              data={block}
              account={block.account}
              timestamp={block.timestamp}
            />
          );
        
        case 'landing_page_mobile_analysis':
          return (
            <AnalysisBlock
              type="landing_page_mobile_analysis"
              title="Mobile Landing Page Analysis"
              data={block}
              account={block.account}
              timestamp={block.timestamp}
            />
          );
        
        case 'tcpa_optimizations':
          return (
            <AnalysisBlock
              type="tcpa_optimizations"
              title="TCPA Optimization Recommendations"
              data={block}
              account={block.account}
              timestamp={block.timestamp}
            />
          );
        
        case 'budget_allocation_optimizations':
          return (
            <AnalysisBlock
              type="budget_allocation_optimizations"
              title="Budget Allocation Optimization"
              data={block}
              account={block.account}
              timestamp={block.timestamp}
            />
          );
        
        case 'negative_keyword_suggestions':
          return (
            <AnalysisBlock
              type="negative_keyword_suggestions"
              title="Negative Keyword Suggestions"
              data={block}
              account={block.account}
              timestamp={block.timestamp}
            />
          );
        
        // Handle RAG-enhanced responses
        case 'rag_enhanced_response':
          return (
            <div className="bg-purple-50 border border-purple-200 rounded-lg p-4 mb-4">
              <div className="flex items-center mb-2">
                <div className="w-2 h-2 bg-purple-500 rounded-full mr-2"></div>
                <span className="text-sm text-purple-600 font-medium">
                  RAG-Enhanced AI Response
                </span>
              </div>
              <div className="text-sm text-purple-700 mb-3">
                {block.fallback_message || "Generated RAG-enhanced AI response for unmatched action"}
              </div>
              <div className="mt-3">
                <AnalysisBlock
                  type="rag_enhanced"
                  title="AI Analysis with Knowledge Base"
                  data={block.data || block}
                  account={block.account}
                  timestamp={block.timestamp}
                />
              </div>
            </div>
          );
        
        default:
          return <div>Unsupported block type: {block.type}</div>;
      }
    };

  const handleActionClick = async (actionId: string, label: string) => {
    let message = "";
    
    // Handle dynamic actions from backend
    if (actionId === "create_campaign") {
      message = "I want to create a new campaign";
    } else if (actionId === "optimize_ad_creatives") {
      message = "Help me optimize my ad creatives and improve performance";
    } else if (actionId === "set_campaign_budget") {
      message = "I need help setting and optimizing my campaign budget";
    } else if (actionId === "submit_campaign") {
      message = "I want to submit and activate my campaign";
    } else if (actionId === "edit_campaign") {
      message = "I need to edit my existing campaign";
    } else if (actionId === "refresh_data") {
      message = "Please refresh my campaign data";
    } else if (actionId === "view_analytics") {
      message = "Show me my campaign analytics and performance data";
    } else if (actionId === "retry_query") {
      message = "Please retry my previous request";
    } else if (actionId === "contact_support") {
      message = "I need to contact support for help";
    } else if (actionId === "retry_action") {
      message = "Please retry the previous action";
    } else if (actionId === "create_ad") {
      message = "I want to create a new ad";
    } else if (actionId === "generate_images") {
      message = "Generate AI images for my products";
    } else if (actionId === "get_creative_suggestions") {
      message = "Give me creative suggestions for my ads";
    } else if (actionId === "create_adgroup") {
      message = "I want to create a new ad group";
    } else if (actionId === "get_campaigns") {
      message = "Show me my existing campaigns";
    } else if (actionId === "get_ads") {
      message = "Show me my existing ads";
    } else if (actionId === "get_analytics") {
      message = "Show me my performance analytics";
    } else if (actionId === "get_budgets") {
      message = "Show me my budget information";
    } else if (actionId === "pause_campaign") {
      message = "I want to pause a campaign";
    } else if (actionId === "resume_campaign") {
      message = "I want to resume a paused campaign";
    } else if (actionId === "delete_campaign") {
      message = "I want to delete a campaign";
    } else if (actionId === "get_performance") {
      message = "Show me my performance data";
    } else if (actionId === "get_keywords") {
      message = "Show me my keyword information";
    } else if (actionId === "search_kb") {
      message = "Search the knowledge base";
    } else if (actionId === "search_db") {
      message = "Search the database";
    } else if (actionId === "add_kb_document") {
      message = "Add a document to the knowledge base";
    } else if (actionId === "create_dynamic_ad") {
      message = "Create an ad with AI-generated creative suggestions";
    } else if (actionId === "set_budget") {
      message = "I need help setting and managing my campaign budget";
    } else if (actionId === "optimize_campaign") {
      message = "Help me optimize my campaign performance";
    } else {
      // For any other dynamic action, use the label or create a meaningful message
      message = `I want to ${label ? label.toLowerCase() : actionId.replace(/_/g, ' ')}`;
    }
    
    if (message) {
      setInputMessage(message);
      // Trigger the message send
      setTimeout(() => handleSendMessage(), 100);
    }
  };

  return (
    <div className={`flex flex-col h-full ${className}`}>
      {/* Header */}
      <div className="bg-white border-b px-4 py-3">
        <h2 className="text-lg font-semibold">AI Marketing Assistant</h2>
        <p className="text-sm text-gray-600">Ask me about your Google Ads campaigns</p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map(renderMessage)}
        {isLoading && (
          <div className="flex justify-start mb-4">
            <div className="bg-gray-100 rounded-lg px-4 py-2">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="bg-white border-t p-4">
        <div className="flex space-x-2">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            placeholder="Ask about your campaigns, performance, or create new ads..."
            className="flex-1 border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isLoading}
          />
          <button
            onClick={handleSendMessage}
            disabled={isLoading || !inputMessage.trim()}
            className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
};

export default AIChatBox;

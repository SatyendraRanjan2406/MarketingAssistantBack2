import React from 'react';

interface AnalysisItem {
  status: 'info' | 'warning' | 'critical' | 'success';
  message: string;
  recommendations?: string[];
  priority?: 'low' | 'medium' | 'high' | 'critical';
  condition?: string;
  action?: string;
}

interface AnalysisBlockProps {
  type: string;
  title: string;
  data: any;
  account?: string;
  timestamp?: string;
}

const AnalysisBlock: React.FC<AnalysisBlockProps> = ({ type, title, data, account, timestamp }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'critical':
        return 'bg-red-100 border-red-400 text-red-800';
      case 'warning':
        return 'bg-yellow-100 border-yellow-400 text-yellow-800';
      case 'success':
        return 'bg-green-100 border-green-400 text-green-800';
      case 'info':
      default:
        return 'bg-blue-100 border-blue-400 text-blue-800';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical':
        return 'bg-red-500 text-white';
      case 'high':
        return 'bg-orange-500 text-white';
      case 'medium':
        return 'bg-yellow-500 text-white';
      case 'low':
        return 'bg-green-500 text-white';
      default:
        return 'bg-gray-500 text-white';
    }
  };

  const renderAnalysisItem = (key: string, item: AnalysisItem) => (
    <div key={key} className="mb-4 p-4 border rounded-lg">
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center space-x-2">
          <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(item.status)}`}>
            {item.status.toUpperCase()}
          </span>
          {item.priority && (
            <span className={`px-2 py-1 text-xs font-medium rounded-full ${getPriorityColor(item.priority)}`}>
              {item.priority.toUpperCase()}
            </span>
          )}
        </div>
      </div>
      
      <h4 className="font-medium text-gray-900 mb-2">{key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</h4>
      
      {item.condition && (
        <div className="mb-2">
          <span className="text-sm font-medium text-gray-600">Condition:</span>
          <p className="text-sm text-gray-700 ml-2">{item.condition}</p>
        </div>
      )}
      
      {item.action && (
        <div className="mb-2">
          <span className="text-sm font-medium text-gray-600">Action:</span>
          <p className="text-sm text-gray-700 ml-2">{item.action}</p>
        </div>
      )}
      
      <p className="text-gray-700 mb-3">{item.message}</p>
      
      {item.recommendations && item.recommendations.length > 0 && (
        <div>
          <span className="text-sm font-medium text-gray-600">Recommendations:</span>
          <ul className="mt-2 space-y-1">
            {item.recommendations.map((rec, index) => (
              <li key={index} className="text-sm text-gray-700 flex items-start">
                <span className="text-blue-500 mr-2">•</span>
                {rec}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );

  const renderOptimizationItem = (key: string, item: any) => (
    <div key={key} className="mb-4 p-4 border rounded-lg">
      <div className="flex items-start justify-between mb-2">
        <h4 className="font-medium text-gray-900">{key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</h4>
        {item.priority && (
          <span className={`px-2 py-1 text-xs font-medium rounded-full ${getPriorityColor(item.priority)}`}>
            {item.priority.toUpperCase()}
          </span>
        )}
      </div>
      
      <div className="mb-2">
        <span className="text-sm font-medium text-gray-600">Condition:</span>
        <p className="text-sm text-gray-700 ml-2">{item.condition}</p>
      </div>
      
      <div className="mb-2">
        <span className="text-sm font-medium text-gray-600">Action:</span>
        <p className="text-sm text-gray-700 ml-2">{item.action}</p>
      </div>
    </div>
  );

  const renderComparisonItem = (key: string, item: any) => (
    <div key={key} className="mb-4 p-4 border rounded-lg">
      <h4 className="font-medium text-gray-900 mb-2">{key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</h4>
      <p className="text-sm text-gray-700 mb-2">{item.message}</p>
      
      {item.metrics && (
        <div>
          <span className="text-sm font-medium text-gray-600">Metrics:</span>
          <div className="mt-2 flex flex-wrap gap-2">
            {item.metrics.map((metric: string, index: number) => (
              <span key={index} className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded">
                {metric}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );

  const renderOpenAIBlock = (block: any) => {
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
        
      case 'chart':
        return (
          <div className="bg-white rounded-lg border p-4">
            <h4 className="font-medium text-gray-800 mb-3">{block.title}</h4>
            <div className="text-sm text-gray-600 mb-2">
              Chart Type: {block.chart_type}
            </div>
            <div className="bg-gray-50 p-3 rounded text-sm">
              <pre className="whitespace-pre-wrap">{JSON.stringify(block.data, null, 2)}</pre>
            </div>
          </div>
        );
        
      case 'table':
        return (
          <div className="bg-white rounded-lg border p-4">
            <h4 className="font-medium text-gray-800 mb-3">{block.title}</h4>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    {block.headers?.map((header: string, index: number) => (
                      <th key={index} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        {header}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {block.rows?.map((row: any[], rowIndex: number) => (
                    <tr key={rowIndex}>
                      {row.map((cell: any, cellIndex: number) => (
                        <td key={cellIndex} className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {String(cell)}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        );
        
      case 'list':
        return (
          <div className="bg-white rounded-lg border p-4">
            <h4 className="font-medium text-gray-800 mb-3">{block.title}</h4>
            <ul className="space-y-2">
              {block.items?.map((item: string, index: number) => (
                <li key={index} className="flex items-start">
                  <span className="text-blue-500 mr-2">•</span>
                  <span className="text-gray-700">{item}</span>
                </li>
              ))}
            </ul>
          </div>
        );
        
      case 'actions':
        return (
          <div className="bg-white rounded-lg border p-4">
            <h4 className="font-medium text-gray-800 mb-3">{block.title}</h4>
            <div className="flex flex-wrap gap-2">
              {block.items?.map((item: any, index: number) => (
                <button
                  key={index}
                  className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors text-sm"
                >
                  {item.label}
                </button>
              ))}
            </div>
          </div>
        );
        
      default:
        return (
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="text-sm text-gray-600">
              <pre className="whitespace-pre-wrap">{JSON.stringify(block, null, 2)}</pre>
            </div>
          </div>
        );
    }
  };

  const renderAnalysisContent = () => {
    switch (type) {
      case 'audience_analysis':
      case 'creative_fatigue_analysis':
      case 'video_performance_analysis':
      case 'placement_analysis':
      case 'device_performance_analysis':
      case 'time_performance_analysis':
      case 'demographic_analysis':
      case 'competitor_analysis':
      case 'creative_testing':
      case 'technical_compliance':
      case 'audience_insights':
      case 'budget_optimizations':
        return (
          <div className="space-y-4">
            {Object.entries(data).map(([key, value]) => {
              if (key in ['success', 'account', 'timestamp', 'error']) return null;
              return renderAnalysisItem(key, value as AnalysisItem);
            })}
          </div>
        );
        
      case 'rag_enhanced':
        // Handle RAG-enhanced responses with blocks structure
        if (data.blocks && Array.isArray(data.blocks)) {
          return (
            <div className="space-y-4">
              {data.blocks.map((block: any, index: number) => (
                <div key={index} className="border-l-4 border-purple-400 pl-4">
                  {renderOpenAIBlock(block)}
                </div>
              ))}
            </div>
          );
        }
        // Fallback for other RAG response formats
        return (
          <div className="space-y-4">
            {Object.entries(data).map(([key, value]) => {
              if (key in ['success', 'account', 'timestamp', 'error']) return null;
              return renderAnalysisItem(key, value as AnalysisItem);
            })}
          </div>
        );
        
      case 'campaign_optimizations':
      case 'adset_optimizations':
      case 'ad_optimizations':
        return (
          <div className="space-y-4">
            {Object.entries(data).map(([key, value]) => {
              if (key in ['success', 'account', 'timestamp', 'error']) return null;
              return renderOptimizationItem(key, value);
            })}
          </div>
        );
        
      case 'performance_comparison':
        return (
          <div className="space-y-4">
            {Object.entries(data).map(([key, value]) => {
              if (key in ['success', 'account', 'timestamp', 'error', 'comparison_type']) return null;
              return renderComparisonItem(key, value);
            })}
          </div>
        );
        
      default:
        return (
          <div className="text-gray-700">
            <pre className="whitespace-pre-wrap text-sm">{JSON.stringify(data, null, 2)}</pre>
          </div>
        );
    }
  };

  if (data.error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">Analysis Error</h3>
            <div className="mt-2 text-sm text-red-700">{data.error}</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border p-6">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-800">{title}</h3>
        {account && (
          <p className="text-sm text-gray-600">Account: {account}</p>
        )}
        {timestamp && (
          <p className="text-sm text-gray-500">Analysis Time: {new Date(timestamp).toLocaleString()}</p>
        )}
      </div>
      
      {renderAnalysisContent()}
    </div>
  );
};

export default AnalysisBlock;

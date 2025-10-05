# Enhanced LangGraph Workflow Diagram

## 🚀 **Two-Stage Data Processing Workflow**

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           ENHANCED LANGGRAPH WORKFLOW                           │
└─────────────────────────────────────────────────────────────────────────────────┘

START
  │
  ▼
┌─────────────┐
│   CONTEXT   │ ◄─── Load conversation history, accessible customers, user context
└─────────────┘
  │
  ▼
┌─────────────┐
│    CHAT     │ ◄─── Process user query with GPT-4o + tools
└─────────────┘
  │
  ▼
┌─────────────┐
│   TOOLS     │ ◄─── Execute ALL_TOOLS to fetch Google Ads data
└─────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           DECISION NODE                                         │
│                                                                                 │
│  Check user query for analysis keywords:                                        │
│  • "analyze", "compare", "insights", "report", "strategy"                      │
│  • "recommendations", "performance", "trends"                                  │
│                                                                                 │
│  If analysis keywords found → DATA_ANALYSIS                                     │
│  If no analysis keywords → CHAT (continue conversation)                        │
└─────────────────────────────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        DATA_ANALYSIS NODE                                       │
│                                                                                 │
│  🧠 GPT-4o Analysis Engine:                                                    │
│                                                                                 │
│  1. Extract tool results from conversation                                     │
│  2. Create analysis prompt with user query + data                              │
│  3. Generate comprehensive insights:                                           │
│     • Key Performance Metrics                                                  │
│     • Trends and Patterns                                                      │
│     • Insights and Recommendations                                             │
│     • Actionable Strategies                                                    │
│     • Visual representation suggestions                                        │
│                                                                                 │
│  Output: Detailed analysis with actionable insights                            │
└─────────────────────────────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                     REPORT_GENERATION NODE                                      │
│                                                                                 │
│  📊 Professional Report Generator:                                             │
│                                                                                 │
│  1. Take analysis content from previous step                                   │
│  2. Format into professional report structure:                                 │
│     • Executive Summary (2-3 key findings)                                     │
│     • Performance Overview (main metrics & KPIs)                               │
│     • Detailed Analysis (in-depth insights)                                    │
│     • Recommendations (actionable next steps)                                  │
│     • Visual Suggestions (charts/graphs descriptions)                          │
│                                                                                 │
│  Output: Formatted report with clear sections and recommendations              │
└─────────────────────────────────────────────────────────────────────────────────┘
  │
  ▼
END

┌─────────────────────────────────────────────────────────────────────────────────┐
│                              WORKFLOW EXAMPLES                                 │
└─────────────────────────────────────────────────────────────────────────────────┘

## Example 1: "Analyze my campaigns"
```
User Query: "Analyze my campaigns"
    │
    ▼
1. CONTEXT → Load conversation + customer ID
2. CHAT → Process query with GPT-4o
3. TOOLS → Execute get_campaigns, get_performance_data
4. DATA_ANALYSIS → GPT-4o analyzes campaign data
5. REPORT_GENERATION → Create formatted analysis report
6. END → Deliver comprehensive campaign analysis
```

## Example 2: "Compare campaigns over 2 weekends"
```
User Query: "Compare campaigns over 2 weekends and strategy to better them"
    │
    ▼
1. CONTEXT → Load conversation + customer ID
2. CHAT → Process query with GPT-4o
3. TOOLS → Execute get_campaigns, get_performance_data (date ranges)
4. DATA_ANALYSIS → GPT-4o compares weekend performance
5. REPORT_GENERATION → Create comparison report with strategies
6. END → Deliver weekend comparison + improvement strategies
```

## Example 3: "Show me ROAS insights"
```
User Query: "Show me ROAS insights"
    │
    ▼
1. CONTEXT → Load conversation + customer ID
2. CHAT → Process query with GPT-4o
3. TOOLS → Execute get_performance_data, get_campaigns
4. DATA_ANALYSIS → GPT-4o analyzes ROAS metrics
5. REPORT_GENERATION → Create ROAS insights report
6. END → Deliver ROAS analysis with recommendations
```

┌─────────────────────────────────────────────────────────────────────────────────┐
│                              KEY FEATURES                                      │
└─────────────────────────────────────────────────────────────────────────────────┘

✅ **Two-Stage Processing**: Data fetching → Analysis
✅ **Automatic Analysis**: GPT-4o analyzes fetched data
✅ **Professional Reports**: Formatted with sections and recommendations
✅ **Smart Routing**: Analysis keywords trigger enhanced workflow
✅ **Context Preservation**: Maintains conversation history
✅ **Customer ID Persistence**: Remembers selected customer
✅ **Error Handling**: Graceful recovery from failures
✅ **Visual Suggestions**: Describes charts/graphs for better understanding

┌─────────────────────────────────────────────────────────────────────────────────┐
│                            ANALYSIS KEYWORDS                                    │
└─────────────────────────────────────────────────────────────────────────────────┘

The system automatically triggers the enhanced workflow when users ask for:
• "analyze" / "analysis"
• "compare" / "comparison" 
• "insights"
• "report"
• "strategy"
• "recommendations"
• "performance"
• "trends"

┌─────────────────────────────────────────────────────────────────────────────────┐
│                              OUTPUT FORMATS                                    │
└─────────────────────────────────────────────────────────────────────────────────┘

📊 **Reports Include**:
• Executive Summary
• Performance Overview
• Detailed Analysis
• Recommendations
• Visual Suggestions (pie charts, bar graphs, line charts, etc.)

📈 **Analysis Types**:
• Campaign Performance Analysis
• ROAS Optimization
• Budget Allocation Insights
• Keyword Performance Trends
• Demographic Analysis
• Geographic Performance
• Competitive Analysis
• Strategic Recommendations

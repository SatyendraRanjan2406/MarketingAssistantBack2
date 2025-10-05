# LangGraph StateGraph Visual Flow Diagram

## Complete Workflow Visualization

```
                    ┌─────────────────┐
                    │      START      │
                    └─────────┬───────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   [context]     │
                    │  context_node   │
                    │                 │
                    │ • Load history  │
                    │ • Get customers │
                    │ • Build prompt  │
                    └─────────┬───────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   [chat]        │
                    │  chat_node      │
                    │                 │
                    │ • GPT-4o + tools│
                    │ • 15 tools      │
                    │ • Tool calls?   │
                    └─────────┬───────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   [tools]       │
                    │  tool_node      │
                    │                 │
                    │ • Google Ads API│
                    │ • Image gen     │
                    │ • Visualizations│
                    └─────────┬───────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │[data_analysis]  │
                    │data_analysis_   │
                    │     node        │
                    │                 │
                    │ • GPT-4o analysis│
                    │ • Insights      │
                    │ • Recommendations│
                    └─────────┬───────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │[report_generation]│
                    │report_generation_│
                    │     node        │
                    │                 │
                    │ • Formatted     │
                    │   reports       │
                    │ • Charts        │
                    │ • Tables        │
                    └─────────┬───────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │       END       │
                    └─────────────────┘
```

## Decision Node Logic Flow

```
                    ┌─────────────────┐
                    │  decision_node  │
                    └─────────┬───────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ Error count >=  │
                    │   max_retries?  │
                    └─────────┬───────┘
                              │
                    ┌─────────┴───────┐
                    │ YES             │ NO
                    ▼                 ▼
            ┌─────────────┐   ┌─────────────────┐
            │     END     │   │ Check current   │
            └─────────────┘   │     step        │
                              └─────────┬───────┘
                                        │
                                        ▼
                              ┌─────────────────┐
                              │ current_step    │
                              │   routing       │
                              └─────────┬───────┘
                                        │
                    ┌───────────────────┼───────────────────┐
                    │                   │                   │
                    ▼                   ▼                   ▼
            ┌─────────────┐   ┌─────────────────┐   ┌─────────────┐
            │   "start"   │   │"context_enriched"│   │"chat_completed"│
            │     →       │   │       →         │   │      →      │
            │   context   │   │      chat       │   │   tools/end  │
            └─────────────┘   └─────────────────┘   └─────────────┘
                                        │
                                        ▼
                              ┌─────────────────┐
                              │"tools_completed"│
                              │       →         │
                              │data_analysis/   │
                              │     chat        │
                              └─────────────────┘
```

## Tool Categories and Flow

```
                    ┌─────────────────┐
                    │   [tools]       │
                    │  tool_node      │
                    └─────────┬───────┘
                              │
                    ┌─────────┴───────┐
                    │                 │
                    ▼                 ▼
            ┌─────────────┐   ┌─────────────────┐
            │ Google Ads  │   │ Image & Visual  │
            │    Tools    │   │     Tools       │
            │             │   │                 │
            │ • Campaigns │   │ • generate_image│
            │ • Ads       │   │ • improve_image │
            │ • Keywords  │   │ • create_data_  │
            │ • Performance│  │   visualization │
            │ • Demographics│  │ • format_tabular│
            │ • Geographic │  │   _data         │
            └─────────────┘   └─────────────────┘
                    │                 │
                    └─────────┬───────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ Analysis needed?│
                    │ (keywords check)│
                    └─────────┬───────┘
                              │
                    ┌─────────┴───────┐
                    │ YES             │ NO
                    ▼                 ▼
            ┌─────────────┐   ┌─────────────────┐
            │data_analysis│   │      chat       │
            │    node     │   │   (continue)    │
            └─────────────┘   └─────────────────┘
```

## Memory Management Flow

```
                    ┌─────────────────┐
                    │   Memory        │
                    │   System        │
                    └─────────┬───────┘
                              │
                    ┌─────────┴───────┐
                    │                 │
                    ▼                 ▼
            ┌─────────────┐   ┌─────────────────┐
            │ Short-term  │   │  Long-term      │
            │   Memory    │   │   Memory        │
            │             │   │                 │
            │ • MemorySaver│  │ • PostgresStore │
            │ • Thread ID │   │ • User data     │
            │ • Checkpoints│  │ • Customers     │
            │ • State     │   │ • History       │
            └─────────────┘   └─────────────────┘
                    │                 │
                    └─────────┬───────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ Conversation    │
                    │   Persistence   │
                    │                 │
                    │ • Load history  │
                    │ • Save messages │
                    │ • Customer ID   │
                    │ • Context       │
                    └─────────────────┘
```

## Example User Journey Flows

### Flow 1: Simple Query
```
User: "What campaigns do I have?"
                    ┌─────────────────┐
                    │      START      │
                    └─────────┬───────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   [context]     │
                    │ • Load history  │
                    │ • Get customers │
                    └─────────┬───────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   [chat]        │
                    │ • GPT-4o        │
                    │ • No tool calls │
                    └─────────┬───────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │       END       │
                    └─────────────────┘
```

### Flow 2: Data Analysis Request
```
User: "Analyze my campaign performance"
                    ┌─────────────────┐
                    │      START      │
                    └─────────┬───────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   [context]     │
                    └─────────┬───────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   [chat]        │
                    │ • GPT-4o        │
                    │ • Tool calls    │
                    └─────────┬───────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   [tools]       │
                    │ • Fetch data    │
                    └─────────┬───────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │[data_analysis]  │
                    │ • GPT-4o        │
                    │ • Insights      │
                    └─────────┬───────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │[report_generation]│
                    │ • Formatted     │
                    │   report        │
                    └─────────┬───────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │       END       │
                    └─────────────────┘
```

### Flow 3: Image Generation
```
User: "Create a marketing poster"
                    ┌─────────────────┐
                    │      START      │
                    └─────────┬───────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   [context]     │
                    └─────────┬───────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   [chat]        │
                    │ • GPT-4o        │
                    │ • Tool calls    │
                    └─────────┬───────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   [tools]       │
                    │ • generate_image│
                    │ • DALL-E 3      │
                    └─────────┬───────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │       END       │
                    └─────────────────┘
```

## State Transitions

```
State Flow:
start → context_enriched → chat_completed → tools_completed → analysis_completed → report_completed → end

Error Handling:
Any state → error → chat (retry) → end (if max retries)

Conditional Routing:
- chat_completed → tools (if tool_calls) OR end (if no tool_calls)
- tools_completed → data_analysis (if analysis keywords) OR chat (continue)
- analysis_completed → report_generation
- report_completed → end
```

## Key Features Visualization

```
                    ┌─────────────────┐
                    │   Key Features  │
                    └─────────┬───────┘
                              │
                    ┌─────────┴───────┐
                    │                 │
                    ▼                 ▼
            ┌─────────────┐   ┌─────────────────┐
            │ Auto Token  │   │ Customer ID     │
            │   Refresh   │   │ Persistence     │
            │             │   │                 │
            │ • 401/403   │   │ • Detection     │
            │ • Retry     │   │ • Save to DB    │
            │ • Seamless  │   │ • Context       │
            └─────────────┘   └─────────────────┘
                    │                 │
                    ▼                 ▼
            ┌─────────────┐   ┌─────────────────┐
            │ Multi-stage │   │ Visual Content  │
            │   Analysis  │   │   Generation    │
            │             │   │                 │
            │ • Data fetch│   │ • Images        │
            │ • Analysis  │   │ • Charts        │
            │ • Reports   │   │ • Tables        │
            └─────────────┘   └─────────────────┘
```

This visual diagram shows the complete StateGraph flow with all nodes, decision logic, memory management, and example user journeys. The system provides a sophisticated multi-stage workflow that can handle simple queries, complex data analysis, image generation, and comprehensive reporting with full memory persistence and error recovery.

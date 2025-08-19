# Google Ads Marketing Assistant - Database Schema

## Overview
This diagram represents the complete database structure for the Google Ads Marketing Assistant application, showing all models, their relationships, and key attributes.

## Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                    USER (Django Auth)                              │
│  ┌─────────────┐                                                                  │
│  │     id      │ ────┐                                                            │
│  │ username   │     │                                                            │
│  │ email      │     │                                                            │
│  │ password   │     │                                                            │
│  │ is_active  │     │                                                            │
│  └─────────────┘     │                                                            │
└───────────────────────┼────────────────────────────────────────────────────────────┘
                        │
                        │ 1:N
                        ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              GOOGLE_ADS_ACCOUNT                                    │
│  ┌─────────────┐                                                                  │
│  │     id      │ ────┐                                                            │
│  │ customer_id │     │                                                            │
│  │account_name│     │                                                            │
│  │currency_code│     │                                                            │
│  │ time_zone  │     │                                                            │
│  │ is_active  │     │                                                            │
│  │created_at  │     │                                                            │
│  │updated_at  │     │                                                            │
│  └─────────────┘     │                                                            │
└───────────────────────┼────────────────────────────────────────────────────────────┘
                        │
                        │ 1:N
                        ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              GOOGLE_ADS_CAMPAIGN                                   │
│  ┌─────────────┐                                                                  │
│  │     id      │ ────┐                                                            │
│  │campaign_id │     │                                                            │
│  │campaign_name│     │                                                            │
│  │campaign_status│   │                                                            │
│  │campaign_type│     │                                                            │
│  │ start_date │     │                                                            │
│  │  end_date  │     │                                                            │
│  │budget_amount│     │                                                            │
│  │ budget_type│     │                                                            │
│  │created_at  │     │                                                            │
│  │updated_at  │     │                                                            │
│  └─────────────┘     │                                                            │
└───────────────────────┼────────────────────────────────────────────────────────────┘
                        │
                        │ 1:N
                        ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              GOOGLE_ADS_AD_GROUP                                   │
│  ┌─────────────┐                                                                  │
│  │     id      │ ────┐                                                            │
│  │ ad_group_id│     │                                                            │
│  │ad_group_name│     │                                                            │
│  │   status   │     │                                                            │
│  │    type    │     │                                                            │
│  │created_at  │     │                                                            │
│  │updated_at  │     │                                                            │
│  └─────────────┘     │                                                            │
└───────────────────────┼────────────────────────────────────────────────────────────┘
                        │
                        │ 1:N
                        ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              GOOGLE_ADS_KEYWORD                                    │
│  ┌─────────────┐                                                                  │
│  │     id      │ ────┐                                                            │
│  │ keyword_id │     │                                                            │
│  │keyword_text│     │                                                            │
│  │ match_type │     │                                                            │
│  │   status   │     │                                                            │
│  │quality_score│     │                                                            │
│  │created_at  │     │                                                            │
│  │updated_at  │     │                                                            │
│  └─────────────┘     │                                                            │
└───────────────────────┼────────────────────────────────────────────────────────────┘
                        │
                        │ 1:N
                        ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                            GOOGLE_ADS_PERFORMANCE                                  │
│  ┌─────────────┐                                                                  │
│  │     id      │                                                                  │
│  │    date    │                                                                  │
│  │impressions │                                                                  │
│  │   clicks   │                                                                  │
│  │cost_micros │                                                                  │
│  │conversions │                                                                  │
│  │conversion_value│                                                               │
│  │     ctr    │                                                                  │
│  │     cpc    │                                                                  │
│  │     cpm    │                                                                  │
│  │conversion_rate│                                                                │
│  │     roas   │                                                                  │
│  │created_at  │                                                                  │
│  │updated_at  │                                                                  │
│  └─────────────┘                                                                  │
└─────────────────────────────────────────────────────────────────────────────────────┘
                        ▲
                        │
                        │ N:1 (Optional)
                        │
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              GOOGLE_ADS_REPORT                                     │
│  ┌─────────────┐                                                                  │
│  │     id      │                                                                  │
│  │    name    │                                                                  │
│  │report_type │                                                                  │
│  │   status   │                                                                  │
│  │  schedule  │                                                                  │
│  │  last_run  │                                                                  │
│  │  next_run  │                                                                  │
│  │ parameters │                                                                  │
│  │created_at  │                                                                  │
│  │updated_at  │                                                                  │
│  └─────────────┘                                                                  │
└─────────────────────────────────────────────────────────────────────────────────────┘
                        ▲
                        │
                        │ N:1
                        │
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              GOOGLE_ADS_ALERT                                      │
│  ┌─────────────┐                                                                  │
│  │     id      │                                                                  │
│  │ alert_type │                                                                  │
│  │  severity  │                                                                  │
│  │    title   │                                                                  │
│  │   message  │                                                                  │
│  │  is_read   │                                                                  │
│  │is_resolved │                                                                  │
│  │created_at  │                                                                  │
│  │resolved_at │                                                                  │
│  └─────────────┘                                                                  │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

## Model Descriptions

### Core Models

#### 1. **User** (Django Auth)
- **Purpose**: Django's built-in user authentication system
- **Key Fields**: username, email, password, is_active
- **Relationships**: One-to-Many with GoogleAdsAccount

#### 2. **GoogleAdsAccount**
- **Purpose**: Stores Google Ads account information and settings
- **Key Fields**: customer_id, account_name, currency_code, time_zone
- **Relationships**: 
  - Many-to-One with User
  - One-to-Many with GoogleAdsCampaign
  - One-to-Many with GoogleAdsPerformance
  - One-to-Many with GoogleAdsAlert

#### 3. **GoogleAdsCampaign**
- **Purpose**: Manages Google Ads campaigns and their configurations
- **Key Fields**: campaign_id, campaign_name, status, type, budget_amount
- **Relationships**:
  - Many-to-One with GoogleAdsAccount
  - One-to-Many with GoogleAdsAdGroup
  - One-to-Many with GoogleAdsPerformance

#### 4. **GoogleAdsAdGroup**
- **Purpose**: Organizes ads within campaigns
- **Key Fields**: ad_group_id, ad_group_name, status, type
- **Relationships**:
  - Many-to-One with GoogleAdsCampaign
  - One-to-Many with GoogleAdsKeyword
  - One-to-Many with GoogleAdsPerformance

#### 5. **GoogleAdsKeyword**
- **Purpose**: Manages keywords for ad targeting
- **Key Fields**: keyword_id, keyword_text, match_type, quality_score
- **Relationships**:
  - Many-to-One with GoogleAdsAdGroup
  - One-to-Many with GoogleAdsPerformance

### Performance & Analytics Models

#### 6. **GoogleAdsPerformance**
- **Purpose**: Stores daily performance metrics and calculated KPIs
- **Key Fields**: date, impressions, clicks, cost_micros, conversions, ctr, cpc, roas
- **Relationships**:
  - Many-to-One with GoogleAdsAccount (Required)
  - Many-to-One with GoogleAdsCampaign (Optional)
  - Many-to-One with GoogleAdsAdGroup (Optional)
  - Many-to-One with GoogleAdsKeyword (Optional)
- **Special Features**: Auto-calculates derived metrics (CTR, CPC, CPM, ROAS)

### Management & Monitoring Models

#### 7. **GoogleAdsReport**
- **Purpose**: Configures automated reports and scheduling
- **Key Fields**: name, report_type, status, schedule, parameters
- **Relationships**: Many-to-One with User

#### 8. **GoogleAdsAlert**
- **Purpose**: Tracks account alerts, warnings, and notifications
- **Key Fields**: alert_type, severity, title, message, is_read, is_resolved
- **Relationships**: Many-to-One with GoogleAdsAccount

## Key Relationships Summary

### Hierarchical Structure
```
User (1) ──→ GoogleAdsAccount (N)
GoogleAdsAccount (1) ──→ GoogleAdsCampaign (N)
GoogleAdsCampaign (1) ──→ GoogleAdsAdGroup (N)
GoogleAdsAdGroup (1) ──→ GoogleAdsKeyword (N)
```

### Performance Tracking
```
GoogleAdsPerformance (N) ──→ GoogleAdsAccount (1) [Required]
GoogleAdsPerformance (N) ──→ GoogleAdsCampaign (1) [Optional]
GoogleAdsPerformance (N) ──→ GoogleAdsAdGroup (1) [Optional]
GoogleAdsPerformance (N) ──→ GoogleAdsKeyword (1) [Optional]
```

### User Management
```
User (1) ──→ GoogleAdsReport (N)
GoogleAdsAccount (1) ──→ GoogleAdsAlert (N)
```

## Database Design Features

### 1. **Flexible Performance Tracking**
- Performance data can be tracked at any level (account, campaign, ad group, or keyword)
- Optional relationships allow for granular or aggregated reporting

### 2. **Audit Trail**
- All models include created_at and updated_at timestamps
- Performance data includes date for time-series analysis

### 3. **Data Integrity**
- Foreign key constraints ensure referential integrity
- Unique constraints on business identifiers (customer_id, campaign_id, etc.)

### 4. **Scalability**
- Indexed fields for common queries (date, account_id, campaign_id)
- Efficient aggregation queries for dashboard metrics

### 5. **Extensibility**
- JSON fields in reports for flexible parameter storage
- Enum fields for status and type classifications

## Indexes for Performance

```sql
-- Performance data indexes
CREATE INDEX idx_performance_date ON google_ads_performance(date);
CREATE INDEX idx_performance_account_date ON google_ads_performance(account_id, date);
CREATE INDEX idx_performance_campaign_date ON google_ads_performance(campaign_id, date);

-- Account and campaign indexes
CREATE INDEX idx_account_user ON google_ads_account(user_id);
CREATE INDEX idx_campaign_account ON google_ads_campaign(account_id);
CREATE INDEX idx_adgroup_campaign ON google_ads_ad_group(campaign_id);
CREATE INDEX idx_keyword_adgroup ON google_ads_keyword(ad_group_id);
```

## Data Flow

1. **Account Setup**: User connects Google Ads account → Account record created
2. **Data Sync**: Campaigns, ad groups, keywords synced from Google Ads API
3. **Performance Collection**: Daily metrics collected and stored with calculated KPIs
4. **Reporting**: Automated reports generated based on stored data
5. **Monitoring**: Alerts generated for performance issues or account problems

This schema provides a robust foundation for managing Google Ads accounts, tracking performance, and generating insights through a comprehensive dashboard interface.

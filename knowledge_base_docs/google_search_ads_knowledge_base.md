# Google Search Ads - Knowledge Base

## 1. Core Performance Metrics

### Traffic Metrics
- **Impressions (Impr.)**: Total number of times your ads were shown to users
- **Clicks**: Total number of times users clicked on your ads
- **Click-Through Rate (CTR)**: Percentage of impressions that resulted in clicks
  - **Formula**: CTR = (Clicks / Impressions) × 100
  - **Example**: 47 clicks / 1,468 impressions = 3.20%

### Cost Metrics
- **Cost**: Total amount spent on the campaign/ad group in the specified currency
- **Average Cost Per Click (Avg. CPC)**: Average amount paid per click
  - **Formula**: Avg. CPC = Cost / Clicks
  - **Example**: ₹5,152.55 / 47 clicks = ₹109.63
- **Currency Code**: The currency in which costs are reported (INR in this dataset)

### Conversion Metrics
- **Conversions**: Number of completed desired actions (purchases, sign-ups, etc.)
- **View-through Conversions**: Conversions that occurred after seeing but not clicking the ad
- **Cost per Conversion (Cost/Conv.)**: Average cost to achieve one conversion
  - **Formula**: Cost/Conv. = Cost / Conversions
  - **Note**: Shows 0 when no conversions occur
- **Conversion Rate (Conv. Rate)**: Percentage of clicks that resulted in conversions
  - **Formula**: Conv. Rate = (Conversions / Clicks) × 100

## 2. Position and Visibility Metrics

### Ad Position Metrics
- **Impression Share (Abs. Top) %**: Percentage of impressions where your ad appeared in the absolute top position (first ad above organic results)
- **Impression Share (Top) %**: Percentage of impressions where your ad appeared anywhere at the top of the search results page
- **Search Impression Share**: Your impressions divided by the estimated number of impressions you were eligible to receive

### Auction Insights Metrics
- **Search Overlap Rate**: How often another advertiser's ad received an impression in the same auction as yours
- **Position Above Rate**: How often another advertiser's ad was ranked higher than yours when both ads appeared
- **Top of Page Rate**: How often another advertiser's ad appeared at the top of the page
- **Outranking Share**: How often your ad ranked higher than another advertiser's ad, or if your ad showed when theirs didn't

## 3. Keyword and Match Type Classifications

### Keyword Status
- **Not Eligible**: Keyword cannot trigger ads due to various reasons
- **Status Reasons**:
  - "low quality": Poor quality score
  - "campaign paused": Campaign is not active
  - Combined reasons separated by semicolons

### Match Types

#### 1. Exact Match [keyword]
- **Definition**: Ads show only when search query has the same meaning or intent as your keyword
- **Symbol**: Square brackets [digital marketing course]
- **Traffic Volume**: Lowest volume, highest relevance
- **Example from data**: [digital marketing course] triggered by "digital marketing course"
- **Close Variants Include**:
  - Same word order: "digital marketing course"
  - Function words (in, to, for, of): "course for digital marketing"
  - Plurals/singulars: "digital marketing courses"
  - Stemming: "learn digital marketing" → "learning digital marketing"
  - Abbreviations: "digital mktg course"
  - Accents: "café" → "cafe"

#### 2. Phrase Match "keyword"
- **Definition**: Ads show for searches that include the meaning of your keyword
- **Symbol**: Quotation marks "digital marketing course"
- **Traffic Volume**: Medium volume, good relevance
- **Behavior**: Keyword phrase can have additional words before/after
- **Examples of what would match "digital marketing course"**:
  - ✅ "best digital marketing course online"
  - ✅ "digital marketing course for beginners"
  - ✅ "advanced digital marketing course certification"
  - ❌ "digital course for marketing" (word order changed)
  - ❌ "marketing digital course online" (different meaning)

#### 3. Broad Match keyword
- **Definition**: Ads show for searches related to your keyword, including synonyms, related searches, and other relevant variations
- **Symbol**: No symbols digital marketing course
- **Traffic Volume**: Highest volume, variable relevance
- **Behavior**: Uses machine learning to find relevant searches
- **Examples of what would match digital marketing course**:
  - ✅ "online marketing classes"
  - ✅ "internet advertising training"
  - ✅ "social media marketing education"
  - ✅ "learn digital advertising"
  - ⚠️ "marketing jobs" (might be too broad)
  - ⚠️ "business courses" (might be too broad)

## 4. Campaign Structure Metrics

### Campaign Level
- **Campaign State**: Active, Paused, or other status
- **Campaign Type**: Search, Display, etc.
- **Campaign Subtype**: Additional categorization (e.g., "All features")

### Ad Group Level
- **Ad Group State**: Enabled, Paused, etc.
- **Bid Strategy**: How bids are managed (e.g., "Maximise Conversions")
- **Bid Strategy Type**: Manual or automated bidding approach
- **Default Max CPC**: Maximum cost-per-click bid set at ad group level

### Ad Level
- **Ad State**: Enabled, Paused, Removed, etc.
- **Ad Type**: Responsive Search Ad, etc.
- **Headlines 1-15**: Different headline variations with position indicators
- **Descriptions 1-4**: Ad description variations with position indicators

## 5. Mathematical Relationships

### Primary Relationships
- **Cost = Clicks × Avg. CPC**
- **CTR = (Clicks / Impressions) × 100**
- **Conv. Rate = (Conversions / Clicks) × 100**
- **Cost/Conv. = Cost / Conversions**
- **Return on Ad Spend (ROAS) = Revenue / Cost** (when revenue data available)

### Derived Metrics
- **Total Impressions = Sum of all impression values across campaigns/ad groups**
- **Total Clicks = Sum of all click values across campaigns/ad groups**
- **Overall CTR = Total Clicks / Total Impressions × 100**
- **Average Position = Weighted average based on impression share metrics**

### Quality Indicators
- **If CTR > Benchmark CTR** → Good ad relevance
- **If Cost/Conv. < Target CPA** → Efficient conversion acquisition
- **If Impression Share (Top) % > 50%** → Good visibility
- **If Conv. Rate > Industry Average** → Effective landing page/offer

## 6. Automation Decision Rules

### Performance Thresholds
- **Low CTR**: CTR < 2% (industry dependent)
- **High CPC**: Avg. CPC > Target CPC threshold
- **Low Conversion Rate**: Conv. Rate < 1% (adjust based on industry)
- **Poor Position**: Impression Share (Top) % < 30%

### Bidding Logic
- **If Conv. Rate > Target AND Cost/Conv. < Target CPA**:
  → Increase bids to gain more volume

- **If CTR < Threshold OR Cost/Conv. > Target CPA**:
  → Decrease bids or pause keywords

- **If Impression Share < 50% AND performance is good**:
  → Increase budgets or bids

### Keyword Management
- **If Keyword Status = "Not Eligible" AND Reason = "low quality"**:
  → Review ad relevance and landing page

- **If Search Term converts well AND not in keyword list**:
  → Add as new keyword

- **If Search Term has high cost and no conversions**:
  → Add as negative keyword

## 7. Data Validation Rules

### Consistency Checks
- **Clicks should never exceed Impressions**
- **CTR should equal (Clicks/Impressions) × 100**
- **Cost should equal Clicks × Avg. CPC** (within rounding tolerance)
- **Conversion Rate should equal (Conversions/Clicks) × 100**

### Data Quality Flags
- **Zero impressions with active campaigns** → investigate delivery issues
- **High impressions with zero clicks** → poor ad relevance
- **Clicks without corresponding cost** → data sync issues
- **Conversions > Clicks** → tracking problems

## 8. Reporting Aggregations

### Campaign Level Rollups
- **Campaign Clicks = Sum(Ad Group Clicks)**
- **Campaign Impressions = Sum(Ad Group Impressions)**
- **Campaign Cost = Sum(Ad Group Costs)**
- **Campaign CTR = Total Campaign Clicks / Total Campaign Impressions × 100**

### Time-based Analysis
- **Daily performance trends** from "When your ads showed" data
- **Week-over-week and month-over-month comparisons**
- **Seasonality pattern identification**

## 9. Ads Structure and Components

### Ad Types and Structure
#### Responsive Search Ads (RSAs)
- **Definition**: Dynamic ad format that automatically tests different combinations of headlines and descriptions
- **Current Standard**: Primary ad type for Search campaigns (as seen in your data)
- **Machine Learning**: Google's AI determines the best combinations based on search queries
- **Structure from your data**:
  - **Ad Type**: "Responsive search ad"
  - **Headlines**: Up to 15
  - **Descriptions**: Up to 4
  - **URLs**: Final URL, Mobile Final URL, Display URLs
  - **Extensions**: Sitelinks, Phone numbers, Apps

### Headline Architecture
#### Headline Strategy Framework:
- **Position 1-3**: Primary headlines (most frequently shown)
- **Position 4-8**: Supporting headlines (rotate based on relevance)
- **Position 9-15**: Additional variants (less frequently shown)

#### Headline Categories for Automation:
- **Brand Headlines**: "10X Digital Marketing Course", "10X Digital Marketing Training"
- **Differentiator Headlines**: "Don't be an Average Marketer", "Unlike Other Marketing Courses"
- **Benefit Headlines**: "Be Better, Be a 10X Marketer", "Boost Your Marketing Career"
- **Format Headlines**: "Live, Online Marketing Classes", "Online Digital Marketing Class"

#### Headline Optimization Rules:
- **If Headline appears in top 3 positions frequently**:
  → High-performing headline, create variations

- **If Headline rarely appears**:
  → Low relevance, review keyword alignment

- **If Brand headlines getting low impressions**:
  → Increase branded keyword bids

### Description Architecture
#### Description Strategy Framework:
- **Description 1**: Primary value proposition + guarantee
- **Description 2**: Outcome-focused + urgency
- **Description 3**: Brand reinforcement + specific timeline
- **Description 4**: Differentiation + unique selling proposition

#### Description Optimization Rules:
- **If Description shows frequently with high CTR**:
  → Successful messaging, replicate approach

- **If Description contains strong CTA**:
  → Test variations of call-to-action

- **If Description mentions guarantees/outcomes**:
  → Monitor for conversion rate impact

### URL Structure and Tracking
#### URL Best Practices:
**Landing Page Relevance Score**:
- **If URL contains keyword** → +Quality Score points
- **If Path matches ad message** → +Relevance points  
- **If UTM tracking consistent** → +Attribution accuracy

#### URL Optimization Rules:
- **If landing page bounce rate > 70%**:
  → Review URL/page relevance to ad copy

- **If conversion tracking missing UTM parameters**:
  → Standardize tracking template

- **If mobile final URL not optimized**:
  → Create mobile-specific landing pages

### Ad Extensions (Assets)
#### Sitelink Extensions
- **Structure**: Additional links below main ad 
- **Best Practice**: 4-6 sitelinks per campaign/ad group

#### Phone Number Extensions
- **Use Case**: For consultation-based businesses

#### Additional Extensions to Consider:
**Callout Extensions**:
- "100% Money-Back Guarantee"
- "Live Online Classes"
- "6-Month Career Transition"
- "Real-World Projects"

**Structured Snippet Extensions**:
- **Course Types**: SEO, PPC, Social Media, Analytics
- **Formats**: Live Classes, Recorded Sessions, Hands-on Projects
- **Outcomes**: Career Transition, Skill Certification, Portfolio Building

### Ad Performance Analysis Framework
#### Creative Performance Metrics:
**Headline Performance**:
- Impression Share by headline position
- CTR correlation with specific headlines
- Conversion rate by headline combination

**Description Performance**:  
- Message resonance (CTR by description)
- Conversion rate by description type
- Bounce rate correlation with ad copy

#### Asset Combination Optimization:
**High-Performing Combinations**:
- **If (Brand Headline + Guarantee Description) → High CTR**:
  → Create more guarantee-focused copy

- **If (Differentiator Headline + Outcome Description) → High Conv Rate**:
  → Emphasize unique positioning + results

**Low-Performing Combinations**:
- **If (Generic Headline + Weak Description) → Low CTR**:
  → Replace with stronger value propositions

### Ad Copy Testing Framework
#### A/B Testing Structure:
**Test Elements**:
1. **Headline emotion** (aspirational vs. practical)
2. **Description focus** (features vs. benefits vs. outcomes)  
3. **CTA strength** ("Learn More" vs. "Get Started" vs. "Book Free AMA")
4. **Urgency elements** ("Limited Seats" vs. "6-Month Guarantee")

#### Automated Creative Optimization:
- **If Ad Strength = "Poor"**:
  → Add more headline/description variants
  → Ensure keyword inclusion in headlines
  → Diversify messaging themes

- **If Ad Strength = "Good" but CTR < benchmark**:
  → Test emotional vs. rational appeals
  → Test pain-point vs. benefit-focused copy
  → Test urgency vs. trust-building messages

- **If Ad Strength = "Excellent"**:
  → Monitor for ad fatigue (CTR decline over time)
  → Create seasonal/promotional variants
  → Test competitor comparison angles

### Ad Quality and Compliance
#### Quality Score Factors:
- **Expected CTR**: Based on historical keyword/ad performance
- **Ad Relevance**: Keyword alignment with headlines/descriptions
- **Landing Page Experience**: Page relevance and user experience

#### Optimization for Each Factor:
- **Low Expected CTR** → Test new creative approaches
- **Poor Ad Relevance** → Include keywords in headlines
- **Poor Landing Page** → Optimize page load speed and relevance

#### Policy Compliance Automation:
**Monitor for**:
- Misleading claims about outcomes
- Excessive capitalization
- Prohibited characters or symbols  
- Trademark violations
- Inappropriate CTAs

**Auto-flag ads containing**:
- "Guaranteed results" without proper disclaimers
- Income claims without substantiation
- Competitive comparisons without proof

## 10. Audience Targeting and Demographics

### Audience Segment Structure
#### Audience Targeting Modes:
- **Targeting**: Ads only show to people in selected audiences (restrictive)
- **Observation**: Ads show to everyone, but you can see performance by audience (recommended for data gathering)
- **Exclusion**: Prevent ads from showing to specific audiences

### Age Demographics
#### Age Groups 
- 18-24 Years
- 25-34 Years
- 35-44 Years
- 45-54 Years
- 55-64 Years
- 65+ Years

### Gender Demographics
#### Gender Targeting:
- Male
- Female

### Household Income Demographics
#### Income Targeting Strategy:
- **Top 10% Income Bracket** ($100k+ annually):
- **Upper Middle Income** (Top 11-25%):
- **Middle Income** (Top 26-50%):
- **Lower Middle Income** (Top 51-75%):
- **Lower Income Brackets** (Bottom 25%):

### Demographic Performance Monitoring
#### Key Performance Indicators by Demographics:
**Age Performance Metrics**:
- CTR by age group
- Conversion rate by age group  
- Cost per conversion by age group
- Lifetime value by age group

**Gender Performance Metrics**:
- Engagement rate differences
- Ad creative performance by gender
- Landing page behavior differences

**Income Performance Metrics**:
- Course tier selection by income
- Payment method preferences
- Upgrade/upsell rates
- Completion rates by income level

#### Automated Demographic Optimization:
**Daily Monitoring**:
- Performance shifts by demographic
- Audience size changes
- Competition intensity by demographic

**Weekly Analysis**:
- ROI by demographic segment
- Creative performance by audience
- Landing page optimization needs

**Monthly Strategy**:
- Budget reallocation based on demographic performance
- New demographic expansion opportunities
- Audience exclusion recommendations

## 11. Google Ad Account Optimization Checks

### General Settings
**Item**: Campaign > AG > keywords > Ads should follow consistency
**Check**: The ads should reflect consistency in the keyword and the Ad group. Campaign should also house only those AGs that are in a group
**Action**: Read keyword, check whether that keyword exists in Ad copies. Check if Ad group naming is in line with keywords, i.e. the keywords and the Ad group name are in sync.

### Sitelinks
**Item**: Check if 4-6 sitelinks are there
**Action**: Suggest sitelink addition if sitelinks not found.

### Landing Page URL
**Item**: Check if LP URL is working and has relevant keywords
**Action**: Check if URL page content is in sync with keywords. LP best practices recommendations to be suggested.

### Duplicate Keywords
**Item**: Same Keyword should not be present in multiple Ad groups/Campaigns, with same targeting settings. This creates bidding wars internally.
**Action**: Check for duplication and suggest anomalies.

## 12. Analysis Framework

### Performance Comparison Over Time
**M1 to M2 comparison (default), MTD comparison, W1 to W2; D1 to D2**
This can also be prompt based - The user can ask "compare current MTD to last month MTD performance."

#### Metrics Compared by Level:
**Campaign Level**:
- Impressions, CTR, CPC, SI share, Conv rate, conversions, spends, Cost/Conv, ROAS
- **Output**: Raise red flags (Critical, Moderate)

**Ad Group Level**:
- Impressions, CTR, CPC, SI share, Conv rate, conversions, spends, Cost/Conv, ROAS
- **Output**: Raise red flags (Critical, Moderate)

**Keyword Level**:
- Impressions, CTR, CPC, SI share, Conv rate, conversions, spends, Cost/Conv, ROAS
- **Output**: Raise red flags (Critical, Moderate)

### Overall Level Analysis

#### Campaign Level Optimization:
**If a campaign is performing better than other campaigns (Lower CAC, SI ceiling is not reached), and is limited by budget, raise budget**
- **Output**: Campaign budget allocation suggestion

**If a campaign is performing better than other campaigns (Lower CAC, SI ceiling is not reached), and is limited by TCPA, increase TCPA**
- **Output**: Campaign TCPA change suggestion

**If a campaign is performing badly (Higher CAC), apply TCPA**
- **Output**: Campaign apply TCPA suggestion

**If a campaign is performing badly (Higher CAC) and TCPA is applied, lower TCPA**
- **Output**: Lower TCPA suggestion

**If a campaign is performing badly, and budget is high, suggest budget reduction**
- **Output**: Budget reduction suggestion

#### Ad Group Level Optimization:
**If an AG is performing better than other AG (Lower CAC, SI ceiling is not reached), and is limited by TCPA, increase TCPA**
- **Output**: AG TCPA change suggestion

**If an AG is performing badly (Higher CAC) and TCPA is applied, lower TCPA**
- **Output**: AG TCPA change suggestion

#### Keyword Trends:
**Are there high potential keywords that are increasing in search volumes but they aren't added**
- **Output**: Suggestion to add certain keywords based on trends.

### Auction Insights
#### Competition Analysis:
**Check campaigns and Ad groups where Competition is eating disproportionately into your SI share**
For top 3 SI share competitors, check their Search ads in Google transparency center - https://adstransparency.google.com/?region=IN
Display a few of their ads and create a summary of what Ads they are placing out for competing keywords.

**Output**: Summary similar to what this tool generates - https://www.gumloop.com/interface/Meta-Ad-Analyzer-rVgiVXjnd6kArr4sht6wVH

### Search Term Report
#### Negative Keyword Management:
**Search terms with 0 conversions and not excluded should be excluded**
Poor performing conversion rate keywords should also be suggested in a potential exclusion list.
- **Output**: Negative keyword exclusion suggestion lists as outputs.

**High CAC, low conversions**
- **Output**: Negative keyword exclusion suggestion

### When Ads Showed Analysis
#### Hour of the Day Analysis:
**X campaigns**
- **Output**: Suggestions for changing bidding settings based on when is the right time to overbid

#### Device Analysis:
**Bid Adjustment based on which device has better results**
- **Output**: Suggestion on increasing/decreasing bidding for devices

#### Location Analysis:
**See which cities are doing better and which ones worse**
- **Output**: Suggestions to exclude/include cities in campaigns or try separate campaigns for top cities to maximize conversions.

### Landing Page Analysis
#### Mobile Speed Score:
**Raise flag for < 7/10 scores**
- **Output**: Mobile optimization recommendations

---

**Last Updated**: December 2024  
**Version**: 1.0.0  
**Category**: Google Ads Knowledge Base  
**Tags**: performance metrics, optimization, bidding, keywords, match types, ad structure, demographics, analysis framework

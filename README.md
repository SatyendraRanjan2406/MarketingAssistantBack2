# Google Ads Marketing Assistant

A comprehensive Django-based application for managing Google Ads accounts, campaigns, and performance data with a modern dashboard interface.

## Features

- **Account Management**: Connect and manage multiple Google Ads accounts
- **Campaign Management**: Create, edit, and monitor campaigns
- **Performance Analytics**: Track impressions, clicks, conversions, and ROI
- **Real-time Dashboard**: Beautiful charts and metrics visualization
- **API Integration**: Full REST API for programmatic access
- **Automated Sync**: Sync data from Google Ads API automatically
- **Reporting**: Generate custom reports and exports
- **Alerts**: Monitor account health and performance issues

## Prerequisites

- Python 3.8+
- Django 5.2+
- Google Ads API access
- Redis (for Celery background tasks)

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd marketing_assistant
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the project root with the following variables:
   ```bash
   # Google Ads API Configuration
   GOOGLE_ADS_CLIENT_ID=your_client_id_here
   GOOGLE_ADS_CLIENT_SECRET=your_client_secret_here
   GOOGLE_ADS_REFRESH_TOKEN=your_refresh_token_here
   GOOGLE_ADS_LOGIN_CUSTOMER_ID=your_login_customer_id_here
   
   # Redis configuration
   REDIS_URL=redis://localhost:6379/0
   
   # Django secret key
   DJANGO_SECRET_KEY=your_secret_key_here
   ```

5. **Run database migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start the development server**
   ```bash
   python manage.py runserver
   ```

## Google Ads API Setup

1. **Get Developer Token**
   - Visit [Google Ads API Center](https://developers.google.com/google-ads/api/docs/first-call/dev-token)
   - Apply for a developer token
   - The developer token `gWYjv6shHAwonl84JDzhpg` is already configured

2. **Create OAuth 2.0 Credentials**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable Google Ads API
   - Create OAuth 2.0 credentials
   - Add authorized redirect URIs

3. **Generate Refresh Token**
   - Use the OAuth 2.0 flow to get a refresh token
   - Store it in your `.env` file

## Usage

### Dashboard
- Access the dashboard at `/google-ads/dashboard/`
- View performance metrics, charts, and account summary
- Monitor campaigns and keywords performance

### API Endpoints

#### Authentication
All API endpoints require authentication. Use Django's session authentication or include credentials in requests.

#### Account Management
- `GET /google-ads/api/accounts/` - List user's Google Ads accounts
- `POST /google-ads/api/accounts/` - Create new account
- `GET /google-ads/api/accounts/{id}/` - Get account details
- `POST /google-ads/api/accounts/{id}/sync/` - Sync account data
- `GET /google-ads/api/accounts/{id}/campaigns/` - Get account campaigns
- `GET /google-ads/api/accounts/{id}/performance/` - Get account performance

#### Campaign Management
- `GET /google-ads/api/campaigns/` - List campaigns
- `POST /google-ads/api/campaigns/` - Create campaign
- `GET /google-ads/api/campaigns/{id}/` - Get campaign details
- `PUT /google-ads/api/campaigns/{id}/` - Update campaign
- `DELETE /google-ads/api/campaigns/{id}/` - Delete campaign
- `POST /google-ads/api/campaigns/{id}/pause/` - Pause campaign
- `POST /google-ads/api/campaigns/{id}/enable/` - Enable campaign
- `GET /google-ads/api/campaigns/{id}/ad-groups/` - Get campaign ad groups
- `GET /google-ads/api/campaigns/{id}/performance/` - Get campaign performance

#### Ad Group Management
- `GET /google-ads/api/ad-groups/` - List ad groups
- `POST /google-ads/api/ad-groups/` - Create ad group
- `GET /google-ads/api/ad-groups/{id}/` - Get ad group details
- `PUT /google-ads/api/ad-groups/{id}/` - Update ad group
- `DELETE /google-ads/api/ad-groups/{id}/` - Delete ad group
- `GET /google-ads/api/ad-groups/{id}/keywords/` - Get ad group keywords
- `GET /google-ads/api/ad-groups/{id}/performance/` - Get ad group performance

#### Keyword Management
- `GET /google-ads/api/keywords/` - List keywords
- `POST /google-ads/api/keywords/` - Create keyword
- `GET /google-ads/api/keywords/{id}/` - Get keyword details
- `PUT /google-ads/api/keywords/{id}/` - Update keyword
- `DELETE /google-ads/api/keywords/{id}/` - Delete keyword
- `GET /google-ads/api/keywords/{id}/performance/` - Get keyword performance

#### Performance Data
- `GET /google-ads/api/performance/` - List performance data
- `GET /google-ads/api/performance/summary/` - Get performance summary
- `GET /google-ads/api/export-performance/` - Export performance data

#### Dashboard
- `GET /google-ads/api/dashboard/` - Get dashboard metrics

#### Account Sync
- `POST /google-ads/api/sync-account/` - Sync account data from Google Ads

#### Campaign Creation
- `POST /google-ads/api/create-campaign/` - Create new campaign

#### Keyword Creation
- `POST /google-ads/api/create-keyword/` - Create new keyword

### Example API Usage

#### Sync Account Data
```bash
curl -X POST http://localhost:8000/google-ads/api/sync-account/ \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=your_session_id" \
  -d '{"customer_id": "1234567890", "force_sync": false}'
```

#### Get Dashboard Metrics
```bash
curl http://localhost:8000/google-ads/api/dashboard/?days=30 \
  -H "Cookie: sessionid=your_session_id"
```

#### Create Campaign
```bash
curl -X POST http://localhost:8000/google-ads/api/create-campaign/ \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=your_session_id" \
  -d '{
    "account": 1,
    "campaign_name": "Summer Sale 2024",
    "campaign_type": "SEARCH",
    "start_date": "2024-06-01",
    "budget_amount": 100.00,
    "budget_type": "DAILY"
  }'
```

## Models

### GoogleAdsAccount
- Stores Google Ads account information
- Links to user accounts
- Tracks account status and settings

### GoogleAdsCampaign
- Campaign details and settings
- Budget and scheduling information
- Performance metrics aggregation

### GoogleAdsAdGroup
- Ad group configuration
- Links to campaigns
- Performance tracking

### GoogleAdsKeyword
- Keyword information
- Match types and quality scores
- Performance metrics

### GoogleAdsPerformance
- Daily performance data
- Calculated metrics (CTR, CPC, ROAS)
- Links to accounts, campaigns, ad groups, and keywords

### GoogleAdsReport
- Report configurations
- Scheduling and automation
- Custom parameters

### GoogleAdsAlert
- Account alerts and notifications
- Performance warnings
- Policy violations

## Configuration

### Settings
The application uses Django settings with Google Ads specific configuration:

```python
GOOGLE_ADS_CONFIG = {
    'developer_token': 'gWYjv6shHAwonl84JDzhpg',
    'client_id': os.getenv('GOOGLE_ADS_CLIENT_ID'),
    'client_secret': os.getenv('GOOGLE_ADS_CLIENT_SECRET'),
    'refresh_token': os.getenv('GOOGLE_ADS_REFRESH_TOKEN'),
    'login_customer_id': os.getenv('GOOGLE_ADS_LOGIN_CUSTOMER_ID'),
}
```

### Environment Variables
- `GOOGLE_ADS_CLIENT_ID`: OAuth 2.0 client ID
- `GOOGLE_ADS_CLIENT_SECRET`: OAuth 2.0 client secret
- `GOOGLE_ADS_REFRESH_TOKEN`: OAuth 2.0 refresh token
- `GOOGLE_ADS_LOGIN_CUSTOMER_ID`: Manager account ID
- `REDIS_URL`: Redis connection string
- `DJANGO_SECRET_KEY`: Django secret key

## Development

### Running Tests
```bash
python manage.py test google_ads_app
```

### Code Quality
The project follows Django best practices and includes:
- Comprehensive model relationships
- Proper API serialization
- Error handling and logging
- Admin interface customization
- REST API with proper authentication

### Database
- SQLite for development (default)
- PostgreSQL for production
- Automatic migrations
- Performance indexes on key fields

## Production Deployment

1. **Set DEBUG=False** in production settings
2. **Use PostgreSQL** for production database
3. **Configure Redis** for Celery background tasks
4. **Set up proper logging** and monitoring
5. **Use HTTPS** for all API endpoints
6. **Implement rate limiting** for API calls
7. **Set up monitoring** for Google Ads API quotas

## Troubleshooting

### Common Issues

1. **Google Ads API Authentication**
   - Verify OAuth credentials
   - Check refresh token validity
   - Ensure proper scopes are granted

2. **Database Issues**
   - Run migrations: `python manage.py migrate`
   - Check database connection
   - Verify model relationships

3. **Performance Issues**
   - Check Redis connection for Celery
   - Monitor Google Ads API quotas
   - Optimize database queries

### Logs
Check Django logs and Google Ads API logs for detailed error information.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions:
- Check the documentation
- Review API responses and error messages
- Check Google Ads API documentation
- Open an issue on GitHub

## Changelog

### Version 1.0.0
- Initial release
- Google Ads API integration
- Dashboard interface
- Complete CRUD operations
- Performance tracking
- Account synchronization

# Google Ads API Documentation Constants

This file contains constants for all Google Ads API documentation URLs, organized for easy access and usage.

## 📁 **File Location**
```
google_ads_new/constants.py
```

## 🔧 **Available Constants**

### **1. Complete URL List**
```python
GOOGLE_ADS_API_DOCS_URLS
```
- **Type**: `List[str]`
- **Description**: Complete list of all Google Ads API documentation URLs
- **Count**: 43 URLs
- **Usage**: When you need to iterate through all documentation URLs

### **2. Categorized URLs**
```python
GOOGLE_ADS_DOCS_CATEGORIES
```
- **Type**: `Dict[str, Union[str, Dict[str, str]]]`
- **Description**: URLs organized by category for easy access
- **Structure**:
  ```python
  {
      'release_notes': "https://...",
      'start': "https://...",
      'videos': "https://...",
      'get_started': {
          'introduction': "https://...",
          'dev_token': "https://...",
          # ... more get started URLs
      },
      'oauth': {
          'overview': "https://...",
          'cloud_project': "https://...",
          # ... more OAuth URLs
      },
      # ... more categories
  }
  ```

### **3. Quick Access URLs**
```python
GOOGLE_ADS_DOCS_QUICK_ACCESS
```
- **Type**: `Dict[str, str]`
- **Description**: Most commonly used documentation URLs
- **Includes**:
  - Getting started
  - Dev token setup
  - OAuth setup
  - First API call
  - Common errors
  - Account management
  - API concepts
  - Mutating data

## 🚀 **Usage Examples**

### **Basic Usage**
```python
from google_ads_new.constants import (
    GOOGLE_ADS_API_DOCS_URLS,
    GOOGLE_ADS_DOCS_CATEGORIES,
    GOOGLE_ADS_DOCS_QUICK_ACCESS
)

# Get all URLs
all_urls = GOOGLE_ADS_API_DOCS_URLS
print(f"Total documentation URLs: {len(all_urls)}")

# Access specific URL
oauth_overview = GOOGLE_ADS_DOCS_CATEGORIES['oauth']['overview']
print(f"OAuth overview: {oauth_overview}")
```

### **Category Access**
```python
# Get all OAuth-related URLs
oauth_urls = GOOGLE_ADS_DOCS_CATEGORIES['oauth']
for key, url in oauth_urls.items():
    print(f"{key}: {url}")

# Get all get-started URLs
get_started_urls = GOOGLE_ADS_DOCS_CATEGORIES['get_started']
for key, url in get_started_urls.items():
    print(f"{key}: {url}")
```

### **Quick Access**
```python
# Get commonly used URLs
dev_token_setup = GOOGLE_ADS_DOCS_QUICK_ACCESS['dev_token_setup']
first_api_call = GOOGLE_ADS_DOCS_QUICK_ACCESS['first_api_call']
common_errors = GOOGLE_ADS_DOCS_QUICK_ACCESS['common_errors']

print(f"Dev token setup: {dev_token_setup}")
print(f"First API call: {first_api_call}")
print(f"Common errors: {common_errors}")
```

### **API Response Integration**
```python
def get_help_urls():
    """Return help URLs for API responses"""
    return {
        'getting_started': GOOGLE_ADS_DOCS_QUICK_ACCESS['getting_started'],
        'oauth_setup': GOOGLE_ADS_DOCS_QUICK_ACCESS['oauth_setup'],
        'common_errors': GOOGLE_ADS_DOCS_QUICK_ACCESS['common_errors'],
        'account_management': GOOGLE_ADS_DOCS_QUICK_ACCESS['account_management']
    }

# Use in API response
def api_error_response(error_type):
    response = {
        'success': False,
        'error': f'Error: {error_type}',
        'help_urls': get_help_urls()
    }
    return response
```

### **Documentation Generation**
```python
def generate_docs_index():
    """Generate a documentation index"""
    index = {}
    
    for category, urls in GOOGLE_ADS_DOCS_CATEGORIES.items():
        if isinstance(urls, dict):
            index[category] = list(urls.keys())
        else:
            index[category] = [urls]
    
    return index
```

## 📋 **Available Categories**

### **Get Started**
- `introduction` - API introduction
- `dev_token` - Developer token setup
- `download_tools` - Download tools and libraries
- `oauth_cloud_project` - OAuth cloud project setup
- `choose_application_type` - Choose application type
- `configure_cloud_project` - Configure cloud project
- `select_account` - Select account
- `make_first_call` - Make first API call
- `common_errors` - Common errors
- `next_steps` - Next steps

### **OAuth**
- `overview` - OAuth overview
- `cloud_project` - OAuth cloud project
- `client_library` - OAuth client library
- `service_accounts` - Service accounts
- `credential_management` - Credential management
- `internals` - OAuth internals
- `2sv` - Two-step verification
- `playground` - OAuth playground

### **Concepts**
- `overview` - API concepts overview
- `api_structure` - API structure
- `versioning` - API versioning
- `changing_objects` - Changing objects
- `retrieving_objects` - Retrieving objects
- `field_service` - Field service
- `call_structure` - Call structure
- `no_developer_token` - No developer token

### **Mutating**
- `overview` - Mutating overview
- `service_mutates` - Service mutates
- `bulk_mutate` - Bulk mutate
- `best_practices` - Best practices

### **Account Management**
- `overview` - Account management overview
- `create_account` - Create account
- `linking_manager_accounts` - Linking manager accounts
- `listing_accounts` - Listing accounts
- `get_account_hierarchy` - Get account hierarchy
- `managing_users` - Managing users
- `managing_invitations` - Managing invitations
- `linking_product_accounts` - Linking product accounts
- `linking_youtube` - Linking YouTube

## 🧪 **Testing**

Run the test script to verify the constants work correctly:

```bash
cd google_ads_new
python test_constants.py
```

## 📝 **Notes**

1. **Maintenance**: URLs are updated as needed when Google releases new documentation
2. **Organization**: URLs are organized logically by functionality and use case
3. **Performance**: Constants are loaded once at import time
4. **Flexibility**: Multiple access patterns available for different use cases
5. **Completeness**: All major Google Ads API documentation URLs are included

## 🔄 **Adding New URLs**

To add new URLs:

1. Add to `GOOGLE_ADS_API_DOCS_URLS` list
2. Add to appropriate category in `GOOGLE_ADS_DOCS_CATEGORIES`
3. Add to `GOOGLE_ADS_DOCS_QUICK_ACCESS` if commonly used
4. Update this documentation
5. Run tests to verify

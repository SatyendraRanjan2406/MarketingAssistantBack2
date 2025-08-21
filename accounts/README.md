# Accounts App

A Django app for user authentication and account management that extends the default Django User model.

## Features

### User Registration
- **Sign Up Form**: Complete registration with fields matching the design image
  - First Name, Last Name
  - Company Name (optional)
  - Email Address
  - Username
  - Password (with confirmation)
  - Terms of Service agreement
- **Form Validation**: Comprehensive validation with error messages
- **Auto-login**: Users are automatically logged in after successful registration

### User Authentication
- **Sign In Form**: Login with username/email and password
- **Remember Me**: Option to stay logged in
- **Forgot Password**: Link for password recovery (placeholder)
- **Secure Logout**: Proper session termination

### User Profile Management
- **Extended Profile**: Additional fields beyond Django's default User model
  - Company Name
  - Phone Number
  - Address
  - Timestamps (created_at, updated_at)
- **Profile Updates**: Edit profile information
- **Password Changes**: Secure password update functionality

### Dashboard
- **Welcome Screen**: Personalized greeting with user information
- **Quick Actions**: Links to key features
- **Navigation**: Easy access to profile and logout

## Models

### UserProfile
Extends the default Django User model with a one-to-one relationship:

```python
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    company_name = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**Features:**
- Automatic creation when a User is created
- Automatic saving when User is updated
- Properties for full_name and display_name

## Forms

### UserRegistrationForm
Custom registration form extending Django's UserCreationForm:

- **Fields**: username, first_name, last_name, email, password1, password2, company_name, phone_number, address
- **Validation**: Email uniqueness, password requirements
- **Styling**: Bootstrap classes and custom placeholders
- **Auto-save**: Creates both User and UserProfile

### UserProfileUpdateForm
Form for updating user profile information:

- **Fields**: first_name, last_name, email, company_name, phone_number, address
- **Auto-populate**: Pre-fills with current values
- **Dual save**: Updates both User and UserProfile models

## Views

### Authentication Views
- `signup_view`: User registration
- `signin_view`: User login
- `signout_view`: User logout

### Profile Views
- `dashboard_view`: User dashboard (login required)
- `profile_view`: Profile editing (login required)
- `change_password_view`: Password change (login required)

### API Views
- `api_signup`: AJAX registration endpoint
- `api_signin`: AJAX login endpoint
- `api_profile_update`: AJAX profile update endpoint

## URLs

```
accounts/
├── signup/                    # User registration
├── signin/                    # User login
├── signout/                   # User logout
├── dashboard/                 # User dashboard
├── profile/                   # Profile management
├── change-password/           # Password change
└── api/
    ├── signup/                # AJAX registration
    ├── signin/                # AJAX login
    └── profile/update/        # AJAX profile update
```

## Templates

### Base Template
- `accounts/base.html`: Simple base template without navigation dependencies

### Authentication Templates
- `accounts/signup.html`: Registration form matching the design image
- `accounts/signin.html`: Login form with consistent styling

### Dashboard Template
- `accounts/dashboard.html`: User dashboard with quick actions

## Admin Integration

### UserAdmin Enhancement
- **Inline Profile**: UserProfile displayed inline with User in admin
- **Company Display**: Company name shown in user list
- **Enhanced Search**: Search by username, email, name, company

### UserProfileAdmin
- **Dedicated Admin**: Separate admin interface for UserProfile
- **Field Grouping**: Organized field sets for better UX
- **Read-only Timestamps**: Created/updated times displayed but not editable

## Security Features

- **CSRF Protection**: All forms include CSRF tokens
- **Password Validation**: Django's built-in password validators
- **Session Management**: Proper login/logout handling
- **Permission Checks**: Login required decorators on protected views

## Styling

### Design Features
- **Modern UI**: Clean, professional appearance
- **Responsive Design**: Works on all device sizes
- **Gradient Backgrounds**: Attractive visual elements
- **Interactive Elements**: Hover effects and animations
- **Form Validation**: Real-time error display

### CSS Framework
- **Bootstrap 5**: Responsive grid and components
- **Custom CSS**: Tailored styling for auth forms
- **Font Awesome**: Icon integration
- **Smooth Transitions**: CSS animations and hover effects

## Usage Examples

### Creating a User Programmatically
```python
from accounts.forms import UserRegistrationForm

form_data = {
    'username': 'john_doe',
    'first_name': 'John',
    'last_name': 'Doe',
    'email': 'john@example.com',
    'password1': 'SecurePass123',
    'password2': 'SecurePass123',
    'company_name': 'Acme Corp'
}

form = UserRegistrationForm(form_data)
if form.is_valid():
    user = form.save()
    print(f"Created user: {user.username}")
    print(f"Company: {user.profile.company_name}")
```

### Accessing User Profile
```python
# In a view or template
user = request.user
if hasattr(user, 'profile'):
    company = user.profile.company_name
    phone = user.profile.phone_number
    full_name = user.profile.full_name
```

### Checking Authentication
```python
from django.contrib.auth.decorators import login_required

@login_required
def protected_view(request):
    # Only authenticated users can access this
    return render(request, 'protected.html')
```

## Integration with Other Apps

The accounts app is designed to work seamlessly with other apps in the project:

- **Google Ads Integration**: Users can connect their Google Ads accounts
- **Campaign Management**: Access to marketing campaign features
- **Analytics**: User-specific data and reports
- **API Access**: Secure endpoints for external integrations

## Future Enhancements

- **Email Verification**: Confirm email addresses during registration
- **Password Reset**: Complete password recovery functionality
- **Social Login**: OAuth integration with Google, Facebook, etc.
- **Two-Factor Authentication**: Enhanced security options
- **User Roles**: Different permission levels for different user types
- **API Keys**: Generate API keys for external integrations

## Testing

To test the accounts app:

1. **Start the server**: `python manage.py runserver`
2. **Visit signup**: `http://localhost:8000/accounts/signup/`
3. **Create an account**: Fill out the registration form
4. **Test login**: `http://localhost:8000/accounts/signin/`
5. **Access dashboard**: `http://localhost:8000/accounts/dashboard/`

## Admin Access

Access the admin interface at `http://localhost:8000/admin/` with:
- Username: `admin2`
- Password: `admin123`

## Dependencies

- Django 5.2+
- Bootstrap 5.3.0
- Font Awesome 6.4.0
- Python 3.8+

A Django app for user authentication and account management that extends the default Django User model.

## Features

### User Registration
- **Sign Up Form**: Complete registration with fields matching the design image
  - First Name, Last Name
  - Company Name (optional)
  - Email Address
  - Username
  - Password (with confirmation)
  - Terms of Service agreement
- **Form Validation**: Comprehensive validation with error messages
- **Auto-login**: Users are automatically logged in after successful registration

### User Authentication
- **Sign In Form**: Login with username/email and password
- **Remember Me**: Option to stay logged in
- **Forgot Password**: Link for password recovery (placeholder)
- **Secure Logout**: Proper session termination

### User Profile Management
- **Extended Profile**: Additional fields beyond Django's default User model
  - Company Name
  - Phone Number
  - Address
  - Timestamps (created_at, updated_at)
- **Profile Updates**: Edit profile information
- **Password Changes**: Secure password update functionality

### Dashboard
- **Welcome Screen**: Personalized greeting with user information
- **Quick Actions**: Links to key features
- **Navigation**: Easy access to profile and logout

## Models

### UserProfile
Extends the default Django User model with a one-to-one relationship:

```python
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    company_name = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**Features:**
- Automatic creation when a User is created
- Automatic saving when User is updated
- Properties for full_name and display_name

## Forms

### UserRegistrationForm
Custom registration form extending Django's UserCreationForm:

- **Fields**: username, first_name, last_name, email, password1, password2, company_name, phone_number, address
- **Validation**: Email uniqueness, password requirements
- **Styling**: Bootstrap classes and custom placeholders
- **Auto-save**: Creates both User and UserProfile

### UserProfileUpdateForm
Form for updating user profile information:

- **Fields**: first_name, last_name, email, company_name, phone_number, address
- **Auto-populate**: Pre-fills with current values
- **Dual save**: Updates both User and UserProfile models

## Views

### Authentication Views
- `signup_view`: User registration
- `signin_view`: User login
- `signout_view`: User logout

### Profile Views
- `dashboard_view`: User dashboard (login required)
- `profile_view`: Profile editing (login required)
- `change_password_view`: Password change (login required)

### API Views
- `api_signup`: AJAX registration endpoint
- `api_signin`: AJAX login endpoint
- `api_profile_update`: AJAX profile update endpoint

## URLs

```
accounts/
├── signup/                    # User registration
├── signin/                    # User login
├── signout/                   # User logout
├── dashboard/                 # User dashboard
├── profile/                   # Profile management
├── change-password/           # Password change
└── api/
    ├── signup/                # AJAX registration
    ├── signin/                # AJAX login
    └── profile/update/        # AJAX profile update
```

## Templates

### Base Template
- `accounts/base.html`: Simple base template without navigation dependencies

### Authentication Templates
- `accounts/signup.html`: Registration form matching the design image
- `accounts/signin.html`: Login form with consistent styling

### Dashboard Template
- `accounts/dashboard.html`: User dashboard with quick actions

## Admin Integration

### UserAdmin Enhancement
- **Inline Profile**: UserProfile displayed inline with User in admin
- **Company Display**: Company name shown in user list
- **Enhanced Search**: Search by username, email, name, company

### UserProfileAdmin
- **Dedicated Admin**: Separate admin interface for UserProfile
- **Field Grouping**: Organized field sets for better UX
- **Read-only Timestamps**: Created/updated times displayed but not editable

## Security Features

- **CSRF Protection**: All forms include CSRF tokens
- **Password Validation**: Django's built-in password validators
- **Session Management**: Proper login/logout handling
- **Permission Checks**: Login required decorators on protected views

## Styling

### Design Features
- **Modern UI**: Clean, professional appearance
- **Responsive Design**: Works on all device sizes
- **Gradient Backgrounds**: Attractive visual elements
- **Interactive Elements**: Hover effects and animations
- **Form Validation**: Real-time error display

### CSS Framework
- **Bootstrap 5**: Responsive grid and components
- **Custom CSS**: Tailored styling for auth forms
- **Font Awesome**: Icon integration
- **Smooth Transitions**: CSS animations and hover effects

## Usage Examples

### Creating a User Programmatically
```python
from accounts.forms import UserRegistrationForm

form_data = {
    'username': 'john_doe',
    'first_name': 'John',
    'last_name': 'Doe',
    'email': 'john@example.com',
    'password1': 'SecurePass123',
    'password2': 'SecurePass123',
    'company_name': 'Acme Corp'
}

form = UserRegistrationForm(form_data)
if form.is_valid():
    user = form.save()
    print(f"Created user: {user.username}")
    print(f"Company: {user.profile.company_name}")
```

### Accessing User Profile
```python
# In a view or template
user = request.user
if hasattr(user, 'profile'):
    company = user.profile.company_name
    phone = user.profile.phone_number
    full_name = user.profile.full_name
```

### Checking Authentication
```python
from django.contrib.auth.decorators import login_required

@login_required
def protected_view(request):
    # Only authenticated users can access this
    return render(request, 'protected.html')
```

## Integration with Other Apps

The accounts app is designed to work seamlessly with other apps in the project:

- **Google Ads Integration**: Users can connect their Google Ads accounts
- **Campaign Management**: Access to marketing campaign features
- **Analytics**: User-specific data and reports
- **API Access**: Secure endpoints for external integrations

## Future Enhancements

- **Email Verification**: Confirm email addresses during registration
- **Password Reset**: Complete password recovery functionality
- **Social Login**: OAuth integration with Google, Facebook, etc.
- **Two-Factor Authentication**: Enhanced security options
- **User Roles**: Different permission levels for different user types
- **API Keys**: Generate API keys for external integrations

## Testing

To test the accounts app:

1. **Start the server**: `python manage.py runserver`
2. **Visit signup**: `http://localhost:8000/accounts/signup/`
3. **Create an account**: Fill out the registration form
4. **Test login**: `http://localhost:8000/accounts/signin/`
5. **Access dashboard**: `http://localhost:8000/accounts/dashboard/`

## Admin Access

Access the admin interface at `http://localhost:8000/admin/` with:
- Username: `admin2`
- Password: `admin123`

## Dependencies

- Django 5.2+
- Bootstrap 5.3.0
- Font Awesome 6.4.0
- Python 3.8+

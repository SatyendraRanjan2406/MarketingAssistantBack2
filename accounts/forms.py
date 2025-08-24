from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class UserRegistrationForm(UserCreationForm):
    """Custom user registration form with additional fields"""
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'John'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Doe'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your@email.com'
        })
    )
    company_name = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your Company'
        })
    )
    phone_number = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+1 (555) 123-4567'
        })
    )
    address = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Enter your address'
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize password field help text
        self.fields['password1'].help_text = 'Must be at least 8 characters with uppercase, lowercase, and number'
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter your password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm your password'
        })
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Choose a username'
        })
    
    def clean_email(self):
        """Ensure email is unique"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email address is already in use.')
        return email
    
    def save(self, commit=True):
        """Save user and create profile"""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            # The signal automatically creates a UserProfile, so we just update it
            if hasattr(user, 'profile'):
                user.profile.company_name = self.cleaned_data.get('company_name', '')
                user.profile.phone_number = self.cleaned_data.get('phone_number', '')
                user.profile.address = self.cleaned_data.get('address', '')
                user.profile.save()
        
        return user


class UserProfileUpdateForm(forms.ModelForm):
    """Form for updating user profile"""
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    
    class Meta:
        # Use string reference to avoid import issues
        model = None  # Will be set in __init__
        fields = ['company_name', 'phone_number', 'address']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set the model dynamically in __init__ to avoid import issues
        from django.apps import apps
        self.Meta.model = apps.get_model('accounts', 'UserProfile')
        
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
    
    def save(self, commit=True):
        """Save profile and update user fields"""
        profile = super().save(commit=False)
        
        if commit:
            # Update user fields
            if profile.user:
                profile.user.first_name = self.cleaned_data['first_name']
                profile.user.last_name = self.cleaned_data['last_name']
                profile.user.email = self.cleaned_data['email']
                profile.user.save()
            
            profile.save()
        
        return profile

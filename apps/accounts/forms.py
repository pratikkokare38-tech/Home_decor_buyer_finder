from django import forms
from django.contrib.auth.models import User
from .models import SellerProfile


class SellerRegistrationForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'seller@example.com'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'})
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'})
    )
    company_name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Artisan Home Goods LLC'})
    )
    from_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Sarah Johnson'})
    )
    postal_address = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': '123 Main Street, Suite 400, Austin, TX 78701'
        })
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username is already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")
        return cleaned_data


class SellerProfileForm(forms.ModelForm):
    class Meta:
        model = SellerProfile
        fields = ['company_name', 'website', 'product_categories', 'from_name', 'from_email', 'postal_address']
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'product_categories': forms.TextInput(attrs={'class': 'form-control'}),
            'from_name': forms.TextInput(attrs={'class': 'form-control'}),
            'from_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'postal_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

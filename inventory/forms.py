from django import forms
from . models import Item, Stock_Transaction, Category
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

class RegisterForm(forms.ModelForm):
    username = forms.CharField(label="username",max_length=150,required=True)
    first_name = forms.CharField(label="first_name",max_length=50,required=True)
    last_name = forms.CharField(label="last_name",max_length=50,required=True)
    email = forms.EmailField(label="email",max_length=100,required=True)
    password1 = forms.CharField(label="Password", min_length=8,required=True,widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm Password", min_length=8,required=True,widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1']

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        email = cleaned_data.get("email")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists")
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 != password2:
            raise forms.ValidationError("Password doesn't match")
        

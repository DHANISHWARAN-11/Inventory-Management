from django import forms
from . models import Item, Stock_Transaction, Category
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

class LoginForm(forms.Form):
    username = forms.CharField(max_length = 100,required=True)
    password = forms.CharField(required=True,widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")
        if not User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username Does Not Exist")
        user = authenticate(username=username, password=password)
        if user is None:
            raise forms.ValidationError("Invalid credentials")

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
        
class ItemForm(forms.ModelForm):
    name = forms.CharField(label = "Name", max_length=10,required=True)
    category = forms.ModelChoiceField(label = "Category",queryset = Category.objects.all(),required = True)
    sku = forms.CharField(required=False)
    description = forms.CharField(label = "Description", max_length=256, required=False)  # make optional
    unit = forms.CharField(label = "Unit", max_length=50, required=True)
    current_stock = forms.IntegerField(label="Current Stock",required=False)  # make optional

    class Meta:
        model= Item
        fields = ['name','category','sku','description','unit','current_stock']

    def clean(self):
        cleaned_data = super().clean()
        item = str(self.cleaned_data.get('name')).lower()
        if Item.objects.filter(name = item).exists():
            raise forms.ValidationError("This item is already exist")

    def clean_description(self):
        return self.cleaned_data.get('description') or None

    def clean_current_stock(self):
        stock = self.cleaned_data.get('current_stock')
        if stock not in [None,'']:
            return int(stock)
        else:
            return 0

class AddReduceForm(forms.ModelForm):
    item = forms.ModelChoiceField(label = "Item", queryset = Item.objects.all(),required=True)
    category = forms.ModelChoiceField(label = "Category",queryset = Category.objects.all(),required = True)
    transaction_type = forms.CharField(label = "Transaction", required=True)
    quantity = forms.IntegerField(label = "Quantity", required=True)
    reference_note = forms.CharField(label = "Reference Note",max_length = 100,required=False)

    class Meta:
        model = Stock_Transaction
        fields = ['item', 'transaction_type', 'quantity','reference_note']

class AddReduceAlterForm(forms.ModelForm):
    category = forms.CharField(label = "Category",required = True)
    item = forms.ModelChoiceField(label = "Item",queryset=Item.objects.all(),widget=forms.HiddenInput())
    transaction_type = forms.CharField(label = "Transaction", required=True)
    quantity = forms.IntegerField(label = "Quantity", required=True)

    class Meta:
        model = Stock_Transaction
        fields = ['category','item','transaction_type','quantity']


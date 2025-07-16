from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=200,null=True,blank=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User,on_delete=models.CASCADE,null=True,related_name='categories_owned')

    def __str__(self):
        return self.name

class Item(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    sku = models.CharField(max_length=8)
    description = models.CharField(max_length=200,null=True,blank=True)  
    unit = models.CharField(max_length=50,blank=True, null=True)
    current_stock = models.IntegerField(default=0)  # allow blank/null, default 0
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, default='active')  # e.g., 'active', 'inactive' 
    
    def __str__(self):
        return self.name
    
class Stock_Transaction(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=10) # eg : 'IN' or 'OUT'
    quantity = models.IntegerField()
    reference_note = models.CharField(max_length=100,blank=True)
    transaction_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.transaction_type
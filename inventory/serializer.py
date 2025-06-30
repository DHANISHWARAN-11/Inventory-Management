from rest_framework import serializers
from .models import Category , Item, Stock_Transaction 

class CategorySerializer(serializers.ModelSerializer):
    item_count = serializers.IntegerField(read_only=True)
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'item_count']

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id','name','category','current_stock']

class AddReduceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock_Transaction
        fields = ['item', 'quantity']
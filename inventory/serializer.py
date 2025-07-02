import random
from rest_framework import serializers
from .models import Category , Item, Stock_Transaction 

class CategoryListSerializer(serializers.ModelSerializer):  # Dashboard Category List
    item_count = serializers.IntegerField(read_only=True)
    class Meta:
        model = Category
        fields = '__all__'

class CategoryCrudSerializer(serializers.ModelSerializer):    #add Category
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']

class ItemListSerializer(serializers.ModelSerializer):  # Dashboard Item List
    class Meta:
        model = Item
        fields = "__all__"

class DashboardAddReduceCrudSerializer(serializers.ModelSerializer):
    transaction_type = serializers.CharField(source='get_transaction_type')

    class Meta:
        model = Stock_Transaction
        fields = ['item', 'quantity', 'transaction_type']

    def validate(self, data):
        item = data['item']
        transaction_type = self.initial_data.get('transaction_type')  # get from raw data
        quantity = data['quantity']

        if quantity <= 0:
            raise serializers.ValidationError("Quantity must be positive.")

        if transaction_type == 'reduce' and item.current_stock < quantity:
            raise serializers.ValidationError("Not enough stock to reduce.")

        # Pass transaction_type forward
        data['transaction_type'] = transaction_type
        return data

    def create(self, validated_data):
        item = validated_data['item']
        quantity = validated_data['quantity']
        transaction_type = validated_data['transaction_type']

        # Update stock
        if transaction_type == 'add':
            item.current_stock += quantity
        elif transaction_type == 'reduce':
            item.current_stock -= quantity
        item.save()

        # Create transaction
        transaction = Stock_Transaction.objects.create(
            item=item,
            transaction_type=transaction_type,
            quantity=quantity
        )
        return transaction


class AddItemCrudSerializer(serializers.ModelSerializer): # Add Item
    class Meta:
        model = Item
        fields = ['id','name','category','current_stock','unit','description']
        read_only_fields = ['sku']  # we generate it, not input from user

    def create(self, validated_data):
        name = validated_data['name']
        category = validated_data['category']

        # generate SKU: 2 letters from category + 2 from item + 2 random digits
        cat = category.name[:2].lower()
        itm = name[:2].lower()
        rand = str(random.randint(1000, 9999))
        sku = cat + itm + rand

        # create item with generated SKU
        item = Item.objects.create(sku=sku, **validated_data)
        return item


class AddReduceStockCrudSerializer(serializers.ModelSerializer):   # Add Reduce Stock
    class Meta:
        model = Stock_Transaction
        fields = ['item', 'transaction_type', 'quantity']

    def validate(self, data):
        item = data.get('item')
        transaction_type = data.get('transaction_type')
        quantity = data.get('quantity')

        if item is None or transaction_type is None or quantity is None:
            raise serializers.ValidationError("Item, transaction type and quantity are required.")

        if quantity <= 0:
            raise serializers.ValidationError("Quantity must be positive.")

        if transaction_type == 'reduce' and item.current_stock < quantity:
            raise serializers.ValidationError(f"Not enough stock to reduce in {item.current_stock}")

        return data

    def create(self, validated_data):
        item = validated_data['item']
        quantity = validated_data['quantity']
        transaction_type = validated_data['transaction_type']


        # Update item stock
        if transaction_type == 'add':
            item.current_stock += quantity
        elif transaction_type == 'reduce':
            item.current_stock -= quantity
        item.save()

        # Save transaction
        transaction = Stock_Transaction.objects.create(
            item=item,
            transaction_type=transaction_type,
            quantity=quantity,
            reference_note=str(self.generate_reference_note())
        )
        print("✅ Transaction saved:", transaction)
        return transaction
    def generate_reference_note(self):
        import random
        return random.randint(1000000000, 9999999999)
   

class TransactionListSerializer(serializers.ModelSerializer):  # Transaction List
    item = serializers.CharField(source='item.name')  # ✅ shows item name, not ID

    class Meta:
        model = Stock_Transaction
        fields = ['item', 'transaction_type', 'quantity', 'transaction_date']


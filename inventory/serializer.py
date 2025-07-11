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
        fields = ['id', 'name', 'description','created_by']
    def validate_name(self,value):
        if Category.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError("This category already exists.")
        return value

class ItemListSerializer(serializers.ModelSerializer):  # Dashboard Item List
    class Meta:
        model = Item
        fields = "__all__"

class DashboardAddReduceCrudSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock_Transaction
        fields = ['item', 'quantity', 'transaction_type']

    def validate(self, data):
        item = data.get('item')
        transaction_type = data.get('transaction_type')
        quantity = data.get('quantity')

        if not item:
            raise serializers.ValidationError({'item': "Item is required."})

        if quantity is None or quantity <= 0:
            raise serializers.ValidationError({'quantity': "Quantity must be positive."})

        if transaction_type not in ['add', 'reduce']:
            raise serializers.ValidationError({'transaction_type': "Invalid type."})

        if transaction_type == 'reduce' and item.current_stock < quantity:
            raise serializers.ValidationError({'quantity': "Not enough stock to reduce."})

        return data

    def create(self, validated_data):
        item = validated_data['item']
        quantity = validated_data['quantity']
        transaction_type = validated_data['transaction_type']
        request = self.context.get('request')

        # Update stock
        if transaction_type == 'add':
            item.current_stock += quantity
        elif transaction_type == 'reduce':
            item.current_stock -= quantity
        item.save()

        # ✅ Correct way to generate reference_note
        reference_note = str(self._generate_reference_note())

        return Stock_Transaction.objects.create(
            item=item,
            transaction_type=transaction_type,
            quantity=quantity,
            reference_note=reference_note,
            user=request.user

        )

    def _generate_reference_note(self):
        import random
        return random.randint(1000000000, 9999999999)
    
class AddItemCrudSerializer(serializers.ModelSerializer): # Add Item
    class Meta:
        model = Item
        fields = ['id','name','category','current_stock','unit','description']
        read_only_fields = ['sku']  

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

    def validate(self, data):
        if data['current_stock'] < 0:
            data['current_stock'] = 0  
        return data

class AddReduceStockCrudSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock_Transaction
        fields = ['item', 'transaction_type', 'quantity']

    def validate(self, data):
        item = data.get('item')
        transaction_type = data.get('transaction_type')
        quantity = data.get('quantity')

        if not item:
            raise serializers.ValidationError({'item': "Item is required."})

        if quantity is None or quantity <= 0:
            raise serializers.ValidationError({'quantity': "Quantity must be positive."})

        if transaction_type not in ['add', 'reduce']:
            raise serializers.ValidationError({'transaction_type': "Invalid type."})

        if transaction_type == 'reduce' and item.current_stock < quantity:
            raise serializers.ValidationError({'quantity': "Not enough stock to reduce."})

        return data

    def create(self, validated_data):
        item = validated_data['item']
        quantity = validated_data['quantity']
        transaction_type = validated_data['transaction_type']
        request = self.context.get('request')

        # Update stock
        if transaction_type == 'add':
            item.current_stock += quantity
        elif transaction_type == 'reduce':
            item.current_stock -= quantity
        item.save()

        # ✅ Correct way to generate reference_note
        reference_note = str(self._generate_reference_note())

        return Stock_Transaction.objects.create(
            item=item,
            transaction_type=transaction_type,
            quantity=quantity,
            reference_note=reference_note,
            user=request.user

        )

    def _generate_reference_note(self):
        import random
        return random.randint(1000000000, 9999999999)
    
class TransactionListSerializer(serializers.ModelSerializer):  # Transaction List
    item = serializers.CharField(source='item.name')  # shows item name

    class Meta:
        model = Stock_Transaction
        fields = ['item', 'transaction_type', 'quantity', 'transaction_date']


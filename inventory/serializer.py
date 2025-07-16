import random
from rest_framework import serializers
from .models import Category , Item, Stock_Transaction 
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMultiAlternatives


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

class ItemDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'name', 'unit', 'current_stock', 'category','status']

class ItemDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'name', 'unit', 'current_stock', 'category', 'status']

    def update(self, instance, validated_data):
        request = self.context.get('request')
        user = request.user if request else None

        previous_stock = instance.current_stock
        current_stock = validated_data.get('current_stock', previous_stock)

        instance = super().update(instance, validated_data)

        # ✅ Send alert if stock falls below the minimum
        minimum_stock = 15
        if current_stock < minimum_stock and user and user.email:
            context = {
                'user_name': user.username,
                'item_name': instance.name,
                'category_name': instance.category.name,
                'current_stock': current_stock,
                'minimum_stock': minimum_stock,
                'dashboard_url': 'http://127.0.0.1:8000/dashboard/',
            }

            subject = "⚠️ Low Stock Alert"
            from_email = 'dhanishwaranb@gmail.com'  # Replace with your sender email
            to_email = [user.email]

            # Load HTML email content
            html_content = render_to_string('email.html', context)

            # Fallback plain text
            text_content = (
                f"Hello {context['user_name']},\n\n"
                f"The stock for the item '{context['item_name']}' under the category '{context['category_name']}' "
                f"has dropped to {context['current_stock']}.\n"
                f"Please avoid going below minimum stock: {context['minimum_stock']}.\n\n"
                f"Dashboard: {context['dashboard_url']}\n\n"
                "This is an automated message. Please do not reply."
            )

            # Send email
            email = EmailMultiAlternatives(subject, text_content, from_email, to_email)
            email.attach_alternative(html_content, "text/html")
            email.send(fail_silently=True)

        return instance


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
        user = request.user

        # Update stock
        if transaction_type == 'add':
            item.current_stock += quantity
        elif transaction_type == 'reduce':
            item.current_stock -= quantity
        item.save()

        # Send low stock alert if below threshold
        if item.current_stock < 15:
            subject = "⚠️ Low Stock Alert"
            html_message = render_to_string("email.html", {
                "user_name": user.username,
                "item_name": item.name,
                "category_name": item.category.name,
                "current_stock": item.current_stock,
                "minimum_stock":15,
                "dashboard_url": f"{settings.SITE_URL}/dashboard/"
            })
            plain_message = (
                f"Hello {user.username},\n\n"
                f"The stock for the item '{item.name}' in category '{item.category.name}' "
                f"has dropped to {item.current_stock}.\n"
                f"Please restock soon.\n\n"
                f"Go to your dashboard to manage inventory: {settings.SITE_URL}/dashboard/\n\n"
                "Thank you for using Mini Inventory Tracker.\n(This is an automated message.)"
            )

            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=True
            )

        # Reference Note
        reference_note = str(self._generate_reference_note())

        return Stock_Transaction.objects.create(
            item=item,
            transaction_type=transaction_type,
            quantity=quantity,
            reference_note=reference_note,
            user=user
        )

    def _generate_reference_note(self):
        import random
        return random.randint(1000000000, 9999999999)

    
class AddItemCrudSerializer(serializers.ModelSerializer):  # Add Item
    class Meta:
        model = Item
        fields = ['id', 'name', 'category', 'current_stock', 'unit', 'description']
        read_only_fields = ['sku']  

    def create(self, validated_data):
        name = validated_data['name']
        category = validated_data['category']

        # generate SKU: 2 letters from category + 2 from item + 4 random digits
        cat = category.name[:2].lower()
        itm = name[:2].lower()
        rand = str(random.randint(1000, 9999))
        sku = cat + itm + rand

        item = Item.objects.create(sku=sku, **validated_data)
        return item

    def validate_current_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("Current stock cannot be negative.")
        return value

    def validate(self, data):
        # Optional: normalize fields here if needed
        return data



class TransactionListSerializer(serializers.ModelSerializer):  # Transaction List
    item = serializers.CharField(source='item.name')  # shows item name

    class Meta:
        model = Stock_Transaction
        fields = ['item', 'transaction_type', 'quantity', 'transaction_date']


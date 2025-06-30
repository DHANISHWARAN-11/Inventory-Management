from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from rest_framework.decorators import api_view 
from rest_framework.response import Response
from inventory.serializer import AddReduceSerializer, CategorySerializer, ItemSerializer
from .models import Category, Item, Stock_Transaction
from .forms import AddReduceForm, ItemForm , AddReduceAlterForm , LoginForm , RegisterForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from django.shortcuts import redirect
import random , csv
from django.db.models import Sum, Count, Avg, Max, Min
from rest_framework import status
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
# Create your views here.

def login(request):
    return render(request,'login.html')

def register(request):
    form = RegisterForm()
    if request.method=='POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data['password1']
            user.set_password(password)
            user.save()
            messages.success(request, "Registered Succesfully")
            return redirect('login')
    return render(request, 'register.html', {'form': form})

# dashboard
@api_view(['GET' , 'POST'])
def category_list(request):
    if request.method  == 'GET':
       categories = Category.objects.annotate(item_count=Count('item')).order_by('id')
       serializer = CategorySerializer(categories, many=True)
       return Response(serializer.data)
    elif request.method == 'POST':
       serializer = CategorySerializer(data=request.data)
       if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
       return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
def dashboard(request):
       if not request.user.is_authenticated:
              return redirect('login') 
       return render(request, 'dashboard.html')
def add_category(request):
       if not request.user.is_authenticated:
              return redirect('login')
       return render(request, 'categorys.html')




@api_view(['GET'])
def items_by_category(request, category_id):
    items = Item.objects.filter(category_id=category_id)
    serializer = ItemSerializer(items, many=True)
    return Response(serializer.data)
def items(request, category_id):
    if not request.user.is_authenticated:
              return redirect('login')
    return render(request, 'dashboard.html')






def add_items(request):
       if not request.user.is_authenticated:
              return redirect('login')
       form = ItemForm()
       categories = Category.objects.all()
       if request.method == 'POST':
              form = ItemForm(request.POST)
              if form.is_valid():
                     sku = ''
                     category = str(form.cleaned_data['category'])
                     name = str(form.cleaned_data['name']).lower()
                     sku += category[0:2].lower()+name[0:2]
                     number = str(random.randint(1000,9999))
                     sku += number
                     item = form.save(commit = False)
                     item.sku = sku
                     item.name = name
                     item.save()
                     messages.success(request, f'Items in {category} Submitted Successfully')
                     return redirect('dashboard')
       return render(request, 'add_items.html',{'categories':categories,'form':form}) 


def add_reduce_stock(request):
       if not request.user.is_authenticated:
              return redirect('login')
       form = AddReduceForm()
       categories = Category.objects.all()
       items = Item.objects.none()  # Default: empty list
       selected_category_id = None
       if request.method == 'POST':
              form = AddReduceForm(request.POST)
              selected_category_id = request.POST.get('category')
              item_id = request.POST.get('item')
              quantity = request.POST.get('quantity')
              transaction_type = request.POST.get('transaction_type')
              if selected_category_id and not transaction_type:
                     items = Item.objects.filter(category_id=selected_category_id)
                     return render(request, 'add_reduce_stock.html', {
                            'categories': categories,
                            'items': items,
                            'selected_category_id': selected_category_id
                     })
              if form.is_valid():
              # Handle actual stock transaction
                     if selected_category_id and item_id and quantity and transaction_type:
                            item = Item.objects.get(pk=item_id)
                            quantity = int(quantity)
                            if item.current_stock > 0:
                                   if transaction_type == 'add':
                                          item.current_stock += quantity
                                          item.save()
                                          transaction = form.save(commit=False)
                                          transaction.reference_note = random.randint(1000000000,9999999999) 
                                          transaction.save()
                                          messages.success(request, f"{quantity} units added to {item.name}.")      
                                   elif transaction_type == 'reduce':
                                          if item.current_stock >= quantity:
                                                 item.current_stock -= quantity
                                                 item.save()
                                                 transaction = form.save(commit=False)
                                                 transaction.reference_note = random.randint(1000000000,9999999999) 
                                                 transaction.save()
                                                 messages.success(request, f"{quantity} units reduced from {item.name}.")
                                                 print(f"{quantity} units reduced to {item.name} total {item.current_stock}")
                                          else:
                                                 messages.error(request, f"Cannot reduce {quantity}. Only {item.current_stock} available.")
                                                 print("Error in Reducing Stock")
                                   return redirect('dashboard')
                            elif item.current_stock <= 0:
                                   if transaction_type == 'add':
                                          item.current_stock += quantity
                                          item.save()
                                          messages.success(request, f"{quantity} units added to {item.name}.")
                                          return redirect('dashboard')
                                   else:
                                          print("Error")
                                          messages.error(request,"Error")
       return render(request, 'add_reduce_stock.html', {'categories': categories,'items': items,'selected_category_id': selected_category_id})


def stock_transaction(request):
       if not request.user.is_authenticated:
              return redirect('login')
       transactions = Stock_Transaction.objects.all()
       return render(request,'transaction.html',{'transactions':transactions})


def download_stock_report(request):
       if not request.user.is_authenticated:
              return redirect('login')
       response = HttpResponse(content_type='text/csv')
       response['Content-Disposition'] = 'attachment; filename="stock_report.csv"'

       writer = csv.writer(response)

       # Header
       writer.writerow(['Item', 'Category', 'Transaction Type', 'Quantity', 'Date'])

       # Data rows
       transactions = Stock_Transaction.objects.select_related('item', 'item__category')
       for tx in transactions:
              writer.writerow([
              tx.item.name,
              tx.item.category.name,
              tx.transaction_type,
              tx.quantity,
              tx.transaction_date,
              ])

       writer.writerow([])
       writer.writerow(['--- Summary ---'])

       # Aggregates for 'Add'
       add_queryset = Stock_Transaction.objects.filter(transaction_type='add')
       add_stats = add_queryset.aggregate(
              total=Sum('quantity'),
              count=Count('id'),
              avg=Avg('quantity'),
              max_qty=Max('quantity'),
              min_qty=Min('quantity')
       )

       # Aggregates for 'Reduce'
       reduce_queryset = Stock_Transaction.objects.filter(transaction_type='reduce')
       reduce_stats = reduce_queryset.aggregate(
              total=Sum('quantity'),
              count=Count('id'),
              avg=Avg('quantity'),
              max_qty=Max('quantity'),
              min_qty=Min('quantity')
       )

       # Get item names for max/min
       add_max_item = add_queryset.filter(quantity=add_stats['max_qty']).first()
       add_min_item = add_queryset.filter(quantity=add_stats['min_qty']).first()
       reduce_max_item = reduce_queryset.filter(quantity=reduce_stats['max_qty']).first()
       reduce_min_item = reduce_queryset.filter(quantity=reduce_stats['min_qty']).first()

       # Write Add section
       writer.writerow(['Add Transactions'])
       writer.writerow(['Total Quantity', add_stats['total'] or 0])
       writer.writerow(['Count', add_stats['count'] or 0])
       writer.writerow(['Average Quantity', round(add_stats['avg'] or 0, 2)])
       writer.writerow(['Max Quantity', f"{add_stats['max_qty']} (Item: {add_max_item.item.name if add_max_item else 'N/A'})"])
       writer.writerow(['Min Quantity', f"{add_stats['min_qty']} (Item: {add_min_item.item.name if add_min_item else 'N/A'})"])

       writer.writerow([])

       # Write Reduce section
       writer.writerow(['Reduce Transactions'])
       writer.writerow(['Total Quantity', reduce_stats['total'] or 0])
       writer.writerow(['Count', reduce_stats['count'] or 0])
       writer.writerow(['Average Quantity', round(reduce_stats['avg'] or 0, 2)])
       writer.writerow(['Max Quantity', f"{reduce_stats['max_qty']} (Item: {reduce_max_item.item.name if reduce_max_item else 'N/A'})"])
       writer.writerow(['Min Quantity', f"{reduce_stats['min_qty']} (Item: {reduce_min_item.item.name if reduce_min_item else 'N/A'})"])

       return response


def add_reduce_stock_alter(request, category, item_name, type):
    if not request.user.is_authenticated:
              return redirect('login')
    items = get_object_or_404(Item, name=item_name)
    context = {
        'c': category,
        'i': item_name,
        't': type,
        'items': items,
    }
    return render(request, 'add_reduce_alter.html', context)

# Handles AJAX POST request from the form
@api_view(['POST'])
def add_reduce_list(request):
    serializer = AddReduceSerializer(data=request.data)
    if serializer.is_valid():
        item = serializer.validated_data['item']
        quantity = serializer.validated_data['quantity']
        tx_type = request.data.get('type')

        if tx_type not in ['add', 'reduce']:
            return Response({'error': 'Invalid transaction type'}, status=400)

        if tx_type == 'add':
            item.current_stock += quantity
        elif tx_type == 'reduce':
            if item.current_stock >= quantity:
                item.current_stock -= quantity
            else:
                return Response({'error': f'Cannot reduce {quantity}. Only {item.current_stock} available.'}, status=400)

        item.save()

        transaction = serializer.save(reference_note=random.randint(1000000000, 9999999999))
        return Response({'message': f"{quantity} units {'added to' if tx_type == 'add' else 'reduced from'} {item.name}", "item": item.id})

    return Response(serializer.errors, status=400)

def logout(request):
       response = redirect('login')
       response.delete_cookie('jwt')
       return response


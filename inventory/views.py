import random
from urllib.parse import unquote
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from rest_framework.decorators import  APIView
from rest_framework.response import Response
from inventory.models import Category, Item, Stock_Transaction
from inventory.serializer import  AddItemCrudSerializer, CategoryCrudSerializer, CategoryListSerializer, ItemDetailSerializer, ItemListSerializer,DashboardAddReduceCrudSerializer, TransactionListSerializer
from .forms import RegisterForm
from django.contrib import messages
from django.shortcuts import redirect
import csv 
from django.db.models import Sum, Count, Avg, Max, Min,Q
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import logout as auth_logout
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import RetrieveUpdateDestroyAPIView


# Create your views here.

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
    return render(request, 'register.html',{'form':form})

def login(request):
    return render(request,'login.html')

# Dashboard Rendering
def dashboard(request, category_id=None):
    return render(request, 'dashboard.html', {'category_id': category_id})

class CategoryListAPIView(APIView): 
    permission_classes = [IsAuthenticated]
    def get(self, request): 
        if request.user.is_superuser:
            categories = Category.objects.all().annotate(item_count=Count('item',filter=Q(item__status='active'))).order_by('id')
        else:
            categories = Category.objects.filter(user=request.user).annotate(item_count=Count('item',filter=Q(item__status='active'))).order_by('id')    
        serializer = CategoryListSerializer(categories, many=True)
        return Response(serializer.data)
    
class ItemListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        category_id = request.GET.get("category_id")
        search_term = request.GET.get("search", "").strip()

        # Filter based on user and category
        items = Item.objects.filter(user=request.user, category_id=category_id,status='active').order_by('name')

        # Apply search if present
        if search_term:
            items = items.filter(name__icontains=search_term)

        paginator = StandardItemsSetPagination()
        paginated_items = paginator.paginate_queryset(items, request)

        serializer = ItemListSerializer(paginated_items, many=True)
        return paginator.get_paginated_response(serializer.data)



class ItemDetailAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Item.objects.all()
    serializer_class = ItemDetailSerializer  # Or use a new one if needed

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def get_serializer_context(self):
        return {'request': self.request}

# Render item form for edit/view/delete
def edit_item(request, item_id):
    return render(request, 'actions.html', {'mode': 'edit', 'item_id': item_id})

def view_item(request, item_id):
    return render(request, 'actions.html', {'mode': 'view', 'item_id': item_id})

def delete_item(request, item_id):
    return render(request, 'actions.html', {'mode': 'delete', 'item_id': item_id})


# Add Category
def add_category(request):
    return render(request, 'categorys.html')
class CategoryCrudAPIView(APIView):
    def post(self, request):
        serializer = CategoryCrudSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user,user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  
# Add Item 
def add_items(request):
    return render(request, 'add_items.html') 

class AddItemCrudAPIView(APIView):
    def post(self, request):
        serializer = AddItemCrudSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({'status': 1, 'message': 'Item added successfully', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Dashboard Add_Reduce
def add_reduce_stock_alter(request, category=None, item_name=None, type=None):
    context = {}
    try:
        category = unquote(category)
        item_name = unquote(item_name)

        item = Item.objects.filter(
            name__iexact=item_name,
            category__name__iexact=category,
            ).first()

        if item:
            context['category_name'] = category
            context['item_name'] = item.name
            context['transaction_type'] = type
            context['item_id'] = item.id
        else:
            context['error'] = " Item not found for given user/category/name."
           
    except Exception as e:
        context['error'] = f"Unexpected error: {str(e)}"
    return render(request, 'add_reduce_alter.html', context)


class DashboardAddReduceCrudAPIView(APIView):
    def post(self, request):
        serializer = DashboardAddReduceCrudSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Stock updated successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Transaction
def stock_transaction(request):
       return render(request, "transaction.html")

class StandardItemsSetPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100
    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'page_size': self.page.paginator.per_page,  # 👈 Add this
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'page_size': self.page.paginator.per_page,  # 👈 Add this
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })
class TransactionListAPIView(APIView): 
    def get(self, request):
        transactions = Stock_Transaction.objects.all().order_by('-transaction_date')
        paginator = StandardResultsSetPagination()
        result_page = paginator.paginate_queryset(transactions, request)
        serializer = TransactionListSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

# Download Report
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

# Logout
def logout(request):
    auth_logout(request)
    return redirect('login')


# CSV Export for Items
class ExportItemsCSVAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        category_id = request.GET.get('category_id')  # optional
        search = request.GET.get('search', '')        # ✅ added

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="items.csv"'

        writer = csv.writer(response)
        writer.writerow(['Category', 'Item_Name', 'Unit', 'Current_Stock'])

        items = Item.objects.select_related('category').filter(user=request.user,status='active')

        if category_id:
            items = items.filter(category_id=category_id)

        if search:
            items = items.filter(name__icontains=search)

        items = items.order_by('category__name', 'name')

        for item in items:
            writer.writerow([item.category.name, item.name, item.unit, item.current_stock])

        return response


class CategoryItemCSVImportAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        print("Incoming data:", request.data)  # Debug log
        rows = request.data.get("rows", [])
        user = request.user

        if not rows or not isinstance(rows, list):
            return Response({"success": False, "message": "Empty or invalid CSV data."}, status=400)

        for row in rows:
            try:
                cat_name = str(row.get("category", "")).strip() or "Unnamed Category"
                item_name = str(row.get("item_name", "")).strip() or "Unnamed Item"
                stock = int(row.get("current_stock", 0))
                unit = str(row.get("unit", "")).strip() or None

                category, _ = Category.objects.get_or_create(name=cat_name, user=user)

                if not Item.objects.filter(name=item_name, category=category, user=user).exists():
                    cat_part = cat_name.lower()[:2].ljust(2, 'x')
                    item_part = item_name.lower()[:2].ljust(2, 'x')
                    random_number = str(random.randint(1000, 9999))
                    sku = f"{cat_part}{item_part}{random_number}"

                    # Ensure SKU is unique
                    while Item.objects.filter(sku=sku).exists():
                        sku = f"{cat_part}{item_part}{random.randint(1000, 9999)}"

                    Item.objects.create(
                        name=item_name,
                        current_stock=stock,
                        category=category,
                        user=user,
                        sku=sku,
                        unit=unit
                    )
            except Exception as e:
                print("Error in row:", row)
                print("Exception:", e)
                return Response({"success": False, "message": f"Error in row: {row}, {str(e)}"}, status=400)

        return Response({"success": True, "message": "Data imported successfully."})

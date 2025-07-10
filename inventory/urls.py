from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView


urlpatterns = [
    # Login Template
    path('',views.login,name='login'),
    # Login API
    path('api/token/',TokenObtainPairView.as_view(),name="Token"),

    # Register Form
    path('register/',views.register, name='register'),

    # DashBoard Template
    path('dashboard/',views.dashboard, name='dashboard'),
    # Category Data API
    path('api/categories/', views.CategoryListAPIView.as_view(), name='category-api'),
    #dashboard item-list
    path('api/items/', views.ItemListAPIView.as_view(), name='item-list'),


    # Add Category Form Template
    path('add_category/',views.add_category, name='add_category'),
    # Adding Category Data API
    path('api/categories/crud', views.CategoryCrudAPIView.as_view(), name='category-api-crud'),

    # Add Item Form Template
    path('add-items/', views.add_items, name='add_items'),
    #items Data API
    path('api/add_items/', views.AddItemCrudAPIView.as_view(), name='api-add-item'),
      

    #dashboard_add_reduce Template
    path('add_reduce_stock/<str:category>/<str:item_name>/<str:type>/', views.add_reduce_stock_alter, name='add_reduce_stock_alter'),
    #dashboard_add_reduce api
    path('api/dashboard_add_reduce_alter/crud/',views.DashboardAddReduceCrudAPIView.as_view(),name='dashboard-add-reduce'),
    
    #add_reduce_stock template
    path('add_reduce_stock/',views.add_reduce_stock,name='add_reduce_stock'),
    #add_reduce_stock api
    path('api/add_reduce_stock/', views.AddReduceStockCrudAPIView.as_view(), name='api_add_reduce_stock'),
    

    # Report Download
    path('download-stock-report/', views.download_stock_report, name='download_stock_report'),
    
    # Logout 
    path('logout/',views.logout,name='logout'),

    # Transaction Template
    path('stock_transaction/',views.stock_transaction, name='stock_transaction'),
    #transaction List API
    path('api/transaction/',views.TransactionListAPIView.as_view(),name='api-transaction'),

    #dashboard csv
    path('api/export/items/', views.ExportItemsCSVAPIView.as_view(), name='export_items_csv_api'),
    path('api/import/categories-items/', views.CategoryItemCSVImportAPIView.as_view(), name='import_csv'),

]

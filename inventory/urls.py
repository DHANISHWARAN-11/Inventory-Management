from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView

urlpatterns = [
    path('',views.login,name='login'),
    path('register/',views.register, name='register'),
    path('dashboard/',views.dashboard, name='dashboard'),
    path('add_category/',views.add_category, name='add_category'),
    path('items/<int:category_id>/',views.items, name='items'),
    path('add_items/',views.add_items, name='add_items'),
    path('add_reduce_stock/',views.add_reduce_stock,name='add_reduce_stock'),
    path('stock_transaction/',views.stock_transaction, name='stock_transaction'),
    path('download-stock-report/', views.download_stock_report, name='download_stock_report'),
    path('add_reduce_stock/<str:category>/<str:item_name>/<str:type>',views.add_reduce_stock_alter,name='add_reduce_stock_alter'),
    path('logout/',views.logout,name='logout'),
    path('api/token/',TokenObtainPairView.as_view(),name="Token"),
]

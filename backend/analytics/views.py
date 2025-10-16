# Reference: PROMPT.md → Analytics Module.
# Purpose: Generate and return sales, inventory, and performance metrics as JSON.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Avg, Q, F, Max
from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from orders.models import Order, OrderItem
from products.models import Product
from accounts.models import User

class DashboardStatsView(APIView):
    """
    Main dashboard statistics for admin and manager roles
    Reference: PROMPT.md → Analytics features
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Check if user has permission to view analytics
        if request.user.role not in ['admin', 'manager']:
            return Response({'error': 'Permission denied'}, status=403)
        
        today = timezone.now().date()
        this_month_start = today.replace(day=1)
        last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
        
        # Total sales metrics
        total_revenue = Order.objects.filter(
            status='paid'
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        
        # Monthly sales
        current_month_sales = Order.objects.filter(
            status='paid',
            created_at__date__gte=this_month_start
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        
        # Total orders
        total_orders = Order.objects.filter(status='paid').count()
        
        # Customer count
        customer_count = User.objects.filter(role='customer').count()
        
        # Low stock products
        low_stock_count = Product.objects.filter(
            stock_quantity__lte=F('low_stock_threshold'),
            is_active=True
        ).count()
        
        # Recent orders (last 7 days)
        week_ago = today - timedelta(days=7)
        recent_orders = Order.objects.filter(
            created_at__date__gte=week_ago
        ).count()
        
        return Response({
            'total_revenue': float(total_revenue),
            'current_month_sales': float(current_month_sales),
            'total_orders': total_orders,
            'customer_count': customer_count,
            'low_stock_count': low_stock_count,
            'recent_orders': recent_orders,
        })

class MonthlySalesView(APIView):
    """
    Monthly sales data for charts
    Reference: PROMPT.md → Monthly sales graph (Chart.js)
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if request.user.role not in ['admin', 'manager']:
            return Response({'error': 'Permission denied'}, status=403)
        
        # Get last 12 months of data
        today = timezone.now().date()
        months_data = []
        
        for i in range(12):
            month_start = (today.replace(day=1) - timedelta(days=32*i)).replace(day=1)
            if i == 0:
                month_end = today
            else:
                next_month = month_start.replace(day=28) + timedelta(days=4)
                month_end = (next_month - timedelta(days=next_month.day)).date()
            
            sales = Order.objects.filter(
                status='paid',
                created_at__date__gte=month_start,
                created_at__date__lte=month_end
            ).aggregate(
                total_amount=Sum('total_amount'),
                total_orders=Count('id')
            )
            
            months_data.append({
                'month': month_start.strftime('%B %Y'),
                'sales': float(sales['total_amount'] or 0),
                'orders': sales['total_orders'] or 0
            })
        
        return Response({'monthly_sales': list(reversed(months_data))})

class TopSellingProductsView(APIView):
    """
    Top selling products report
    Reference: PROMPT.md → Top-selling products report
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if request.user.role not in ['admin', 'manager']:
            return Response({'error': 'Permission denied'}, status=403)
        
        # Get top 10 selling products by quantity
        top_products = OrderItem.objects.filter(
            order__status='paid'
        ).values(
            'product__name',
            'product__sku',
            'product__price'
        ).annotate(
            total_sold=Sum('quantity'),
            total_revenue=Sum('total_price')
        ).order_by('-total_sold')[:10]
        
        return Response({'top_products': list(top_products)})

class LowStockSummaryView(APIView):
    """
    Low stock products summary
    Reference: PROMPT.md → Low-stock summary
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if request.user.role not in ['admin', 'manager']:
            return Response({'error': 'Permission denied'}, status=403)
        
        # Get products with low stock
        low_stock_products = Product.objects.filter(
            stock_quantity__lte=F('low_stock_threshold'),
            is_active=True
        ).values(
            'name',
            'sku',
            'stock_quantity',
            'low_stock_threshold',
            'category__name',
            'brand__name'
        ).order_by('stock_quantity')
        
        return Response({'low_stock_products': list(low_stock_products)})

class CustomerFrequencyView(APIView):
    """
    Customer purchase frequency analysis
    Reference: PROMPT.md → Customer frequency analysis
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if request.user.role not in ['admin', 'manager']:
            return Response({'error': 'Permission denied'}, status=403)
        
        # Analyze customer purchase patterns
        customer_stats = User.objects.filter(
            role='customer'
        ).annotate(
            total_orders=Count('orders', filter=Q(orders__status='paid')),
            total_spent=Sum('orders__total_amount', filter=Q(orders__status='paid')),
            last_order_date=Max('orders__created_at', filter=Q(orders__status='paid'))
        ).filter(total_orders__gt=0).order_by('-total_spent')[:20]
        
        customer_data = []
        for customer in customer_stats:
            customer_data.append({
                'customer_name': f"{customer.first_name} {customer.last_name}".strip() or customer.username,
                'total_orders': customer.total_orders,
                'total_spent': float(customer.total_spent or 0),
                'last_order_date': customer.last_order_date.date() if customer.last_order_date else None
            })
        
        return Response({'customer_frequency': customer_data})

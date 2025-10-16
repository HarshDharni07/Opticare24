# Reference: PROMPT.md → Analytics Module → Data Serialization.
# Purpose: Serialize aggregated metric data for analytics dashboards.
# Note: Convert querysets or aggregated data into API-friendly formats (sales, revenue, stock levels).

from rest_framework import serializers
from decimal import Decimal

class DashboardStatsSerializer(serializers.Serializer):
    """
    Serializer for main dashboard statistics
    Reference: PROMPT.md → Analytics features for admin dashboard
    """
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    current_month_sales = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_orders = serializers.IntegerField()
    customer_count = serializers.IntegerField()
    low_stock_count = serializers.IntegerField()
    recent_orders = serializers.IntegerField()
    
    # Additional computed metrics
    average_order_value = serializers.SerializerMethodField()
    sales_growth = serializers.SerializerMethodField()
    
    def get_average_order_value(self, obj):
        """Calculate average order value"""
        if obj.get('total_orders', 0) > 0:
            avg = obj['total_revenue'] / obj['total_orders']
            return float(avg)
        return 0.0
    
    def get_sales_growth(self, obj):
        """Calculate sales growth percentage (placeholder)"""
        # This would require historical comparison
        # For now, return a placeholder value
        return 12.5  # Example growth percentage

class MonthlySalesDataSerializer(serializers.Serializer):
    """
    Serializer for monthly sales data
    Reference: PROMPT.md → Monthly sales graph (Chart.js)
    """
    month = serializers.CharField()
    sales = serializers.DecimalField(max_digits=12, decimal_places=2)
    orders = serializers.IntegerField()
    
    # Additional computed fields for charts
    average_per_order = serializers.SerializerMethodField()
    
    def get_average_per_order(self, obj):
        """Calculate average sales per order for the month"""
        if obj.get('orders', 0) > 0:
            return float(obj['sales'] / obj['orders'])
        return 0.0

class MonthlySalesSerializer(serializers.Serializer):
    """
    Container serializer for monthly sales response
    """
    monthly_sales = MonthlySalesDataSerializer(many=True)

class TopSellingProductSerializer(serializers.Serializer):
    """
    Serializer for top selling products data
    Reference: PROMPT.md → Top-selling products report
    """
    product__name = serializers.CharField(source='name')
    product__sku = serializers.CharField(source='sku')
    product__price = serializers.DecimalField(source='price', max_digits=10, decimal_places=2)
    total_sold = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    
    # Computed fields
    revenue_percentage = serializers.SerializerMethodField()
    
    def get_revenue_percentage(self, obj):
        """Calculate percentage of total revenue (requires context)"""
        # This would need total revenue from context
        return 0.0  # Placeholder

class TopSellingProductsSerializer(serializers.Serializer):
    """
    Container serializer for top selling products response
    """
    top_products = TopSellingProductSerializer(many=True)

class LowStockProductSerializer(serializers.Serializer):
    """
    Serializer for low stock products data
    Reference: PROMPT.md → Low-stock summary
    """
    name = serializers.CharField()
    sku = serializers.CharField()
    stock_quantity = serializers.IntegerField()
    low_stock_threshold = serializers.IntegerField()
    category__name = serializers.CharField(source='category_name')
    brand__name = serializers.CharField(source='brand_name')
    
    # Computed fields
    stock_deficit = serializers.SerializerMethodField()
    urgency_level = serializers.SerializerMethodField()
    
    def get_stock_deficit(self, obj):
        """Calculate how many items short of threshold"""
        return max(0, obj['low_stock_threshold'] - obj['stock_quantity'])
    
    def get_urgency_level(self, obj):
        """Determine urgency level based on stock"""
        stock = obj['stock_quantity']
        threshold = obj['low_stock_threshold']
        
        if stock == 0:
            return 'critical'
        elif stock <= threshold * 0.5:
            return 'high'
        else:
            return 'medium'

class LowStockSummarySerializer(serializers.Serializer):
    """
    Container serializer for low stock summary response
    """
    low_stock_products = LowStockProductSerializer(many=True)
    
    # Summary statistics
    total_products_low = serializers.SerializerMethodField()
    critical_count = serializers.SerializerMethodField()
    estimated_reorder_cost = serializers.SerializerMethodField()
    
    def get_total_products_low(self, obj):
        """Count total products with low stock"""
        return len(obj.get('low_stock_products', []))
    
    def get_critical_count(self, obj):
        """Count products with zero stock"""
        return len([p for p in obj.get('low_stock_products', []) if p['stock_quantity'] == 0])
    
    def get_estimated_reorder_cost(self, obj):
        """Estimate cost to restock all low items (placeholder)"""
        return 15000.00  # Placeholder calculation

class CustomerFrequencySerializer(serializers.Serializer):
    """
    Serializer for customer frequency analysis data
    Reference: PROMPT.md → Customer frequency analysis
    """
    customer_name = serializers.CharField()
    total_orders = serializers.IntegerField()
    total_spent = serializers.DecimalField(max_digits=12, decimal_places=2)
    last_order_date = serializers.DateField(allow_null=True)
    
    # Computed fields
    average_order_value = serializers.SerializerMethodField()
    customer_segment = serializers.SerializerMethodField()
    days_since_last_order = serializers.SerializerMethodField()
    
    def get_average_order_value(self, obj):
        """Calculate average order value for customer"""
        if obj['total_orders'] > 0:
            return float(obj['total_spent'] / obj['total_orders'])
        return 0.0
    
    def get_customer_segment(self, obj):
        """Categorize customer based on spending"""
        total_spent = float(obj['total_spent'])
        if total_spent >= 5000:
            return 'premium'
        elif total_spent >= 2000:
            return 'regular'
        else:
            return 'occasional'
    
    def get_days_since_last_order(self, obj):
        """Calculate days since last order"""
        if obj['last_order_date']:
            from datetime import date
            return (date.today() - obj['last_order_date']).days
        return None

class CustomerFrequencyAnalysisSerializer(serializers.Serializer):
    """
    Container serializer for customer frequency response
    """
    customer_frequency = CustomerFrequencySerializer(many=True)
    
    # Analysis summary
    total_active_customers = serializers.SerializerMethodField()
    average_orders_per_customer = serializers.SerializerMethodField()
    customer_segments_count = serializers.SerializerMethodField()
    
    def get_total_active_customers(self, obj):
        """Count total active customers"""
        return len(obj.get('customer_frequency', []))
    
    def get_average_orders_per_customer(self, obj):
        """Calculate average orders per customer"""
        customers = obj.get('customer_frequency', [])
        if customers:
            total_orders = sum(c['total_orders'] for c in customers)
            return round(total_orders / len(customers), 2)
        return 0.0
    
    def get_customer_segments_count(self, obj):
        """Count customers by segment"""
        customers = obj.get('customer_frequency', [])
        segments = {'premium': 0, 'regular': 0, 'occasional': 0}
        
        for customer in customers:
            total_spent = float(customer['total_spent'])
            if total_spent >= 5000:
                segments['premium'] += 1
            elif total_spent >= 2000:
                segments['regular'] += 1
            else:
                segments['occasional'] += 1
        
        return segments

class SalesMetricsSerializer(serializers.Serializer):
    """
    Serializer for comprehensive sales metrics
    Reference: PROMPT.md → Generate visual analytics on sales
    """
    period = serializers.CharField()
    total_sales = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_orders = serializers.IntegerField()
    unique_customers = serializers.IntegerField()
    average_order_value = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    # Product performance
    top_category = serializers.CharField(allow_null=True)
    top_brand = serializers.CharField(allow_null=True)
    
    # Growth metrics (compared to previous period)
    sales_growth_percentage = serializers.DecimalField(max_digits=5, decimal_places=2, allow_null=True)
    orders_growth_percentage = serializers.DecimalField(max_digits=5, decimal_places=2, allow_null=True)

class InventoryMetricsSerializer(serializers.Serializer):
    """
    Serializer for inventory analytics
    Reference: PROMPT.md → Stock flow tracking and alerts
    """
    total_products = serializers.IntegerField()
    total_stock_value = serializers.DecimalField(max_digits=12, decimal_places=2)
    low_stock_items = serializers.IntegerField()
    out_of_stock_items = serializers.IntegerField()
    
    # Category breakdown
    categories_breakdown = serializers.DictField(child=serializers.IntegerField())
    brands_breakdown = serializers.DictField(child=serializers.IntegerField())
    
    # Stock turnover (placeholder)
    average_stock_turnover = serializers.DecimalField(max_digits=5, decimal_places=2, default=0.0)

class ComprehensiveAnalyticsSerializer(serializers.Serializer):
    """
    Serializer for comprehensive analytics dashboard
    Combines multiple metric types for executive summary
    """
    sales_metrics = SalesMetricsSerializer()
    inventory_metrics = InventoryMetricsSerializer()
    dashboard_stats = DashboardStatsSerializer()
    
    # Executive summary
    business_health_score = serializers.SerializerMethodField()
    key_insights = serializers.SerializerMethodField()
    
    def get_business_health_score(self, obj):
        """Calculate overall business health score (0-100)"""
        # Simple scoring algorithm
        score = 75  # Base score
        
        # Adjust based on metrics
        dashboard = obj.get('dashboard_stats', {})
        if dashboard.get('low_stock_count', 0) > 10:
            score -= 10
        if dashboard.get('recent_orders', 0) > dashboard.get('total_orders', 0) * 0.1:
            score += 10
        
        return max(0, min(100, score))
    
    def get_key_insights(self, obj):
        """Generate key business insights"""
        insights = []
        
        dashboard = obj.get('dashboard_stats', {})
        inventory = obj.get('inventory_metrics', {})
        
        if dashboard.get('low_stock_count', 0) > 5:
            insights.append("Multiple products are running low on stock")
        
        if inventory.get('out_of_stock_items', 0) > 0:
            insights.append(f"{inventory['out_of_stock_items']} products are out of stock")
        
        if not insights:
            insights.append("All systems operating normally")
        
        return insights
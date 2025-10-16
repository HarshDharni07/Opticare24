# Reference: PROMPT.md → Inventory Management Module → Data Serialization.
# Purpose: Serialize and validate product, category, and inventory data for CRUD APIs.
# Note: Ensure image and QR fields are correctly represented with absolute URLs.

from rest_framework import serializers
from .models import Product, Category, Brand

class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for product categories
    Reference: PROMPT.md → products_category
    """
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'product_count', 'created_at']
        read_only_fields = ['created_at']
    
    def get_product_count(self, obj):
        """Return number of active products in this category"""
        return obj.products.filter(is_active=True).count()

class BrandSerializer(serializers.ModelSerializer):
    """
    Serializer for product brands
    Reference: PROMPT.md → products_brand
    """
    logo_url = serializers.SerializerMethodField()
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Brand
        fields = ['id', 'name', 'description', 'logo', 'logo_url', 'product_count', 'created_at']
        read_only_fields = ['created_at']
    
    def get_logo_url(self, obj):
        """Return absolute URL for logo image"""
        if obj.logo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.logo.url)
            return obj.logo.url
        return None
    
    def get_product_count(self, obj):
        """Return number of active products for this brand"""
        return obj.products.filter(is_active=True).count()

class ProductListSerializer(serializers.ModelSerializer):
    """
    Serializer for product list view (minimal data)
    Reference: PROMPT.md → CRUD for product entries
    """
    category_name = serializers.CharField(source='category.name', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    image_url = serializers.SerializerMethodField()
    stock_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'sku', 'product_type', 'category_name', 
            'brand_name', 'price', 'stock_quantity', 'stock_status',
            'image_url', 'is_active', 'created_at'
        ]
    
    def get_image_url(self, obj):
        """Return absolute URL for product image"""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
    
    def get_stock_status(self, obj):
        """Return stock status indicator"""
        if not obj.is_in_stock:
            return 'out_of_stock'
        elif obj.is_low_stock:
            return 'low_stock'
        else:
            return 'in_stock'

class ProductDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed product view
    Reference: PROMPT.md → Product specifications and QR-based SKU
    """
    category = CategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    brand_id = serializers.IntegerField(write_only=True)
    
    image_url = serializers.SerializerMethodField()
    qr_code_url = serializers.SerializerMethodField()
    stock_status = serializers.SerializerMethodField()
    profit_margin = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'sku', 'product_type',
            'category', 'category_id', 'brand', 'brand_id',
            'price', 'cost_price', 'profit_margin',
            'stock_quantity', 'low_stock_threshold', 'stock_status',
            'frame_size', 'frame_color', 'lens_type',
            'image', 'image_url', 'qr_code_path', 'qr_code_url',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_image_url(self, obj):
        """Return absolute URL for product image"""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
    
    def get_qr_code_url(self, obj):
        """Return absolute URL for QR code image"""
        if obj.qr_code_path:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(f'/media/{obj.qr_code_path}')
            return f'/media/{obj.qr_code_path}'
        return None
    
    def get_stock_status(self, obj):
        """Return detailed stock status"""
        return {
            'is_in_stock': obj.is_in_stock,
            'is_low_stock': obj.is_low_stock,
            'status': 'out_of_stock' if not obj.is_in_stock else (
                'low_stock' if obj.is_low_stock else 'in_stock'
            )
        }
    
    def get_profit_margin(self, obj):
        """Calculate profit margin percentage"""
        if obj.cost_price and obj.cost_price > 0:
            margin = ((obj.price - obj.cost_price) / obj.cost_price) * 100
            return round(margin, 2)
        return 0

class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for product creation and updates
    Reference: PROMPT.md → CRUD for product entries with validation
    """
    class Meta:
        model = Product
        fields = [
            'name', 'description', 'sku', 'product_type',
            'category', 'brand', 'price', 'cost_price',
            'stock_quantity', 'low_stock_threshold',
            'frame_size', 'frame_color', 'lens_type',
            'image', 'is_active'
        ]
    
    def validate_sku(self, value):
        """Ensure SKU is unique"""
        instance = getattr(self, 'instance', None)
        if Product.objects.filter(sku=value).exclude(pk=instance.pk if instance else None).exists():
            raise serializers.ValidationError("Product with this SKU already exists.")
        return value
    
    def validate(self, attrs):
        """Validate price relationships"""
        cost_price = attrs.get('cost_price', 0)
        price = attrs.get('price', 0)
        
        if cost_price and cost_price >= price:
            raise serializers.ValidationError(
                "Selling price must be higher than cost price."
            )
        
        return attrs

class StockUpdateSerializer(serializers.Serializer):
    """
    Serializer for stock quantity updates
    Reference: PROMPT.md → Stock quantity auto-decrement on sale
    """
    quantity = serializers.IntegerField(min_value=1)
    operation = serializers.ChoiceField(choices=['add', 'reduce'])
    reason = serializers.CharField(max_length=200, required=False)
    
    def validate_quantity(self, value):
        """Validate quantity for reduction operations"""
        operation = self.initial_data.get('operation')
        if operation == 'reduce':
            product = self.context.get('product')
            if product and value > product.stock_quantity:
                raise serializers.ValidationError(
                    f"Cannot reduce {value} items. Only {product.stock_quantity} available."
                )
        return value

class LowStockAlertSerializer(serializers.ModelSerializer):
    """
    Serializer for low stock alerts
    Reference: PROMPT.md → Low-stock threshold admin dashboard alert
    """
    category_name = serializers.CharField(source='category.name', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    stock_difference = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'sku', 'category_name', 'brand_name',
            'stock_quantity', 'low_stock_threshold', 'stock_difference'
        ]
    
    def get_stock_difference(self, obj):
        """Return how many items below threshold"""
        return obj.low_stock_threshold - obj.stock_quantity
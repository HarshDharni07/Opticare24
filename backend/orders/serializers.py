# Reference: PROMPT.md → Billing & Warranty Module → Data Serialization.
# Purpose: Serialize orders, items, billing, and warranty information.
# Note: Include nested serializers for related product and user data. Generate computed fields like total_price.

from rest_framework import serializers
from .models import Order, OrderItem
from accounts.serializers import UserProfileSerializer
from products.serializers import ProductListSerializer

class OrderItemSerializer(serializers.ModelSerializer):
    """
    Serializer for order items with product details
    Reference: PROMPT.md → orders_orderitem linked to Products
    """
    product = ProductListSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    total_price = serializers.SerializerMethodField()
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'product_id', 'product_name',
            'quantity', 'unit_price', 'total_price',
            'prescription', 'notes', 'created_at'
        ]
        read_only_fields = ['created_at']
    
    def get_total_price(self, obj):
        """Calculate total price for this item"""
        return float(obj.total_price)
    
    def validate_product_id(self, value):
        """Validate product exists and is active"""
        from products.models import Product
        try:
            product = Product.objects.get(id=value, is_active=True)
            if not product.is_in_stock:
                raise serializers.ValidationError("Product is out of stock")
            return value
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found or inactive")

class OrderListSerializer(serializers.ModelSerializer):
    """
    Serializer for order list view (minimal data)
    Reference: PROMPT.md → orders_order for billing system
    """
    customer_name = serializers.SerializerMethodField()
    staff_name = serializers.SerializerMethodField()
    items_count = serializers.SerializerMethodField()
    final_amount = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_id', 'receipt_number', 'customer_name',
            'staff_name', 'status', 'total_amount', 'final_amount',
            'items_count', 'created_at'
        ]
    
    def get_customer_name(self, obj):
        """Return customer display name"""
        return f"{obj.customer.first_name} {obj.customer.last_name}".strip() or obj.customer.username
    
    def get_staff_name(self, obj):
        """Return staff member display name"""
        if obj.staff_member:
            return f"{obj.staff_member.first_name} {obj.staff_member.last_name}".strip() or obj.staff_member.username
        return None
    
    def get_items_count(self, obj):
        """Return total number of items in order"""
        return obj.items.count()
    
    def get_final_amount(self, obj):
        """Return final amount after discount and tax"""
        return float(obj.final_amount)

class OrderDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed order view
    Reference: PROMPT.md → Order workflow with QR-based bill generation
    """
    customer = UserProfileSerializer(read_only=True)
    staff_member = UserProfileSerializer(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    
    qr_code_url = serializers.SerializerMethodField()
    final_amount = serializers.SerializerMethodField()
    items_summary = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_id', 'receipt_number', 'customer', 'staff_member',
            'status', 'total_amount', 'discount_amount', 'tax_amount',
            'final_amount', 'qr_code_path', 'qr_code_url', 'notes',
            'items', 'items_summary', 'created_at', 'updated_at'
        ]
        read_only_fields = ['order_id', 'receipt_number', 'created_at', 'updated_at']
    
    def get_qr_code_url(self, obj):
        """Return absolute URL for QR code"""
        if obj.qr_code_path:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(f'/media/{obj.qr_code_path}')
            return f'/media/{obj.qr_code_path}'
        return None
    
    def get_final_amount(self, obj):
        """Return final amount after calculations"""
        return float(obj.final_amount)
    
    def get_items_summary(self, obj):
        """Return summary of items in order"""
        total_items = sum(item.quantity for item in obj.items.all())
        unique_products = obj.items.count()
        return {
            'total_items': total_items,
            'unique_products': unique_products
        }

class OrderCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new orders
    Reference: PROMPT.md → Staff creates new order for a customer
    """
    items = OrderItemSerializer(many=True, write_only=True)
    
    class Meta:
        model = Order
        fields = [
            'customer', 'discount_amount', 'tax_amount', 'notes', 'items'
        ]
    
    def validate_items(self, value):
        """Validate order items"""
        if not value:
            raise serializers.ValidationError("Order must have at least one item")
        
        # Check for duplicate products
        product_ids = [item['product_id'] for item in value]
        if len(product_ids) != len(set(product_ids)):
            raise serializers.ValidationError("Duplicate products in order")
        
        return value
    
    def create(self, validated_data):
        """Create order with items"""
        items_data = validated_data.pop('items')
        
        # Calculate total amount from items
        total_amount = 0
        for item_data in items_data:
            from products.models import Product
            product = Product.objects.get(id=item_data['product_id'])
            unit_price = item_data.get('unit_price', product.price)
            total_amount += unit_price * item_data['quantity']
        
        validated_data['total_amount'] = total_amount
        validated_data['staff_member'] = self.context['request'].user
        
        # Create order
        order = Order.objects.create(**validated_data)
        
        # Create order items
        for item_data in items_data:
            product_id = item_data.pop('product_id')
            from products.models import Product
            product = Product.objects.get(id=product_id)
            
            # Set unit price if not provided
            if 'unit_price' not in item_data:
                item_data['unit_price'] = product.price
            
            OrderItem.objects.create(
                order=order,
                product=product,
                **item_data
            )
            
            # Reduce stock
            product.reduce_stock(item_data['quantity'])
        
        return order

class OrderUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating order status and details
    Reference: PROMPT.md → Payment status tracked
    """
    class Meta:
        model = Order
        fields = ['status', 'discount_amount', 'tax_amount', 'notes']
    
    def validate_status(self, value):
        """Validate status transitions"""
        if self.instance:
            current_status = self.instance.status
            
            # Define allowed transitions
            allowed_transitions = {
                'pending': ['paid', 'cancelled'],
                'paid': ['refunded'],
                'cancelled': [],
                'refunded': []
            }
            
            if value not in allowed_transitions.get(current_status, []):
                raise serializers.ValidationError(
                    f"Cannot change status from {current_status} to {value}"
                )
        
        return value

class CartItemSerializer(serializers.Serializer):
    """
    Serializer for cart items (temporary before order creation)
    Reference: PROMPT.md → Cart workflow
    """
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)
    notes = serializers.CharField(max_length=500, required=False, allow_blank=True)
    
    def validate_product_id(self, value):
        """Validate product availability"""
        from products.models import Product
        try:
            product = Product.objects.get(id=value, is_active=True)
            if not product.is_in_stock:
                raise serializers.ValidationError("Product is out of stock")
            return value
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found")

class BillingReceiptSerializer(serializers.ModelSerializer):
    """
    Serializer for generating receipts
    Reference: PROMPT.md → QR-based bill generated
    """
    customer_details = serializers.SerializerMethodField()
    items_details = serializers.SerializerMethodField()
    payment_summary = serializers.SerializerMethodField()
    qr_code_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'receipt_number', 'created_at', 'customer_details',
            'items_details', 'payment_summary', 'qr_code_url', 'notes'
        ]
    
    def get_customer_details(self, obj):
        """Return customer information for receipt"""
        return {
            'name': f"{obj.customer.first_name} {obj.customer.last_name}".strip() or obj.customer.username,
            'email': obj.customer.email,
            'phone': obj.customer.phone,
            'address': obj.customer.address
        }
    
    def get_items_details(self, obj):
        """Return formatted items for receipt"""
        items = []
        for item in obj.items.all():
            items.append({
                'name': item.product.name,
                'sku': item.product.sku,
                'quantity': item.quantity,
                'unit_price': float(item.unit_price),
                'total_price': float(item.total_price)
            })
        return items
    
    def get_payment_summary(self, obj):
        """Return payment breakdown"""
        return {
            'subtotal': float(obj.total_amount),
            'discount': float(obj.discount_amount),
            'tax': float(obj.tax_amount),
            'final_amount': float(obj.final_amount)
        }
    
    def get_qr_code_url(self, obj):
        """Return QR code URL for verification"""
        if obj.qr_code_path:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(f'/media/{obj.qr_code_path}')
        return None
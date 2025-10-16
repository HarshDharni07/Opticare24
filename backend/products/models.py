# Reference: PROMPT.md → Inventory Management Module.
# Purpose: Store product data including brand, category, stock, and QR path.

from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

class Category(models.Model):
    """
    Product categories for optical products (Frames, Lenses, Accessories)
    Reference: PROMPT.md → products_category
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'products_category'
        verbose_name_plural = 'Categories'
    
    def __str__(self):
        return self.name

class Brand(models.Model):
    """
    Product brands for optical products
    Reference: PROMPT.md → products_brand
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to='brands/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'products_brand'
    
    def __str__(self):
        return self.name

class Product(models.Model):
    """
    Main product model for eyewear, lenses, and accessories
    Reference: PROMPT.md → products_product with QR-based SKU identification
    """
    
    PRODUCT_TYPES = [
        ('frames', 'Frames'),
        ('lenses', 'Lenses'),
        ('accessories', 'Accessories'),
        ('sunglasses', 'Sunglasses'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    sku = models.CharField(max_length=50, unique=True, help_text='Stock Keeping Unit')
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPES)
    
    # Relations
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='products')
    
    # Pricing
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    cost_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text='Cost price for profit calculations'
    )
    
    # Inventory tracking
    stock_quantity = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(
        default=10,
        help_text='Alert when stock falls below this level'
    )
    
    # Product specifications
    frame_size = models.CharField(max_length=20, blank=True, null=True)
    frame_color = models.CharField(max_length=50, blank=True, null=True)
    lens_type = models.CharField(max_length=50, blank=True, null=True)
    
    # Media
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    qr_code_path = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        help_text='Path to QR code image for product identification'
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'products_product'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.sku}"
    
    @property
    def is_low_stock(self):
        """Check if product is below low stock threshold"""
        return self.stock_quantity <= self.low_stock_threshold
    
    @property
    def is_in_stock(self):
        """Check if product is in stock"""
        return self.stock_quantity > 0
    
    def reduce_stock(self, quantity):
        """Reduce stock quantity (used in orders)"""
        if self.stock_quantity >= quantity:
            self.stock_quantity -= quantity
            self.save()
            return True
        return False
    
    def add_stock(self, quantity):
        """Add stock quantity"""
        self.stock_quantity += quantity
        self.save()

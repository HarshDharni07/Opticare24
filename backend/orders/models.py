# Reference: PROMPT.md → Billing & Warranty Module.
# Purpose: Define order and order item tables with relations to products and users.

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid

class Order(models.Model):
    """
    Main order model for billing system
    Reference: PROMPT.md → orders_order with QR-based bill generation
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
        ('cancelled', 'Cancelled'),
    ]
    
    order_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text='Unique order identifier'
    )
    
    # Relations
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
        limit_choices_to={'role__in': ['customer']},
        help_text='Customer who placed the order'
    )
    
    staff_member = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_orders',
        limit_choices_to={'role__in': ['staff', 'admin', 'manager']},
        help_text='Staff member who processed the order'
    )
    
    # Order details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    
    tax_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    
    # QR and Receipt
    qr_code_path = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text='Path to QR code for bill verification'
    )
    
    receipt_number = models.CharField(
        max_length=50,
        unique=True,
        help_text='Unique receipt number for printing'
    )
    
    # Notes
    notes = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'orders_order'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order {self.receipt_number} - {self.customer.username}"
    
    @property
    def final_amount(self):
        """Calculate final amount after discount and tax"""
        return self.total_amount - self.discount_amount + self.tax_amount
    
    def save(self, *args, **kwargs):
        if not self.receipt_number:
            # Generate unique receipt number
            import datetime
            today = datetime.date.today()
            prefix = f"RCP{today.strftime('%Y%m%d')}"
            
            # Get last receipt number for today
            last_order = Order.objects.filter(
                receipt_number__startswith=prefix
            ).order_by('-receipt_number').first()
            
            if last_order:
                last_number = int(last_order.receipt_number[-4:])
                new_number = last_number + 1
            else:
                new_number = 1
            
            self.receipt_number = f"{prefix}{new_number:04d}"
        
        super().save(*args, **kwargs)

class OrderItem(models.Model):
    """
    Individual items in an order
    Reference: PROMPT.md → orders_orderitem linked to Products
    """
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text='Price per unit at time of purchase'
    )
    
    # Prescription link (if applicable)
    prescription = models.ForeignKey(
        'prescriptions.Prescription',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text='Associated prescription if product requires one'
    )
    
    # Notes for specific item
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'orders_orderitem'
        unique_together = ['order', 'product']
    
    def __str__(self):
        return f"{self.product.name} x{self.quantity}"
    
    @property
    def total_price(self):
        """Calculate total price for this item"""
        return self.quantity * self.unit_price
    
    def save(self, *args, **kwargs):
        # Set unit price from product if not provided
        if not self.unit_price:
            self.unit_price = self.product.price
        super().save(*args, **kwargs)

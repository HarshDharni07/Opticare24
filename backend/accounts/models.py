# Reference: PROMPT.md → Accounts Module.
# Purpose: Define User model with roles (Admin, Manager, Staff, Optometrist, Customer).

from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Extended user model for OptiCare24 with role-based access control.
    Reference: PROMPT.md → Django's built-in AbstractUser model extended
    """
    
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('manager', 'Manager'),
        ('staff', 'Staff Member'),
        ('optometrist', 'Optometrist'),
        ('customer', 'Customer'),
    ]
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='customer',
        help_text='User role determining access permissions'
    )
    
    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        help_text='Contact phone number'
    )
    
    address = models.TextField(
        blank=True,
        null=True,
        help_text='Physical address'
    )
    
    date_of_birth = models.DateField(
        blank=True,
        null=True,
        help_text='Date of birth for customer records'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'accounts_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    @property
    def is_admin(self):
        return self.role == 'admin'
    
    @property
    def is_manager(self):
        return self.role == 'manager'
    
    @property
    def is_staff_member(self):
        return self.role == 'staff'
    
    @property
    def is_optometrist(self):
        return self.role == 'optometrist'
    
    @property
    def is_customer(self):
        return self.role == 'customer'

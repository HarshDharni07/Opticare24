# Reference: PROMPT.md → Prescription Module.
# Purpose: Store optical prescriptions with references to customer and optometrist.

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class Prescription(models.Model):
    """
    Optical prescription model with eye power measurements
    Reference: PROMPT.md → prescriptions_prescription with customer_id and optometrist_id
    """
    
    # Relations
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='prescriptions',
        limit_choices_to={'role': 'customer'},
        help_text='Customer who owns this prescription'
    )
    
    optometrist = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='issued_prescriptions',
        limit_choices_to={'role': 'optometrist'},
        help_text='Optometrist who issued this prescription'
    )
    
    # Left Eye measurements
    left_eye_sphere = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(-20.0), MaxValueValidator(20.0)],
        help_text='Sphere power for left eye (-20.00 to +20.00)'
    )
    
    left_eye_cylinder = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(-6.0), MaxValueValidator(6.0)],
        help_text='Cylinder power for left eye (-6.00 to +6.00)'
    )
    
    left_eye_axis = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(180)],
        help_text='Axis for left eye (1 to 180 degrees)'
    )
    
    # Right Eye measurements
    right_eye_sphere = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(-20.0), MaxValueValidator(20.0)],
        help_text='Sphere power for right eye (-20.00 to +20.00)'
    )
    
    right_eye_cylinder = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(-6.0), MaxValueValidator(6.0)],
        help_text='Cylinder power for right eye (-6.00 to +6.00)'
    )
    
    right_eye_axis = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(180)],
        help_text='Axis for right eye (1 to 180 degrees)'
    )
    
    # Additional measurements
    pupillary_distance = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        validators=[MinValueValidator(40.0), MaxValueValidator(80.0)],
        help_text='Pupillary distance in millimeters (40.0 to 80.0)'
    )
    
    # Reading addition (for progressive/bifocal lenses)
    add_power = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0.75), MaxValueValidator(3.50)],
        help_text='Additional power for reading (0.75 to 3.50)'
    )
    
    # Prescription details
    prescription_type = models.CharField(
        max_length=20,
        choices=[
            ('distance', 'Distance Vision'),
            ('reading', 'Reading/Near Vision'),
            ('progressive', 'Progressive/Multifocal'),
            ('bifocal', 'Bifocal'),
        ],
        default='distance'
    )
    
    # Notes and validity
    additional_notes = models.TextField(
        blank=True,
        null=True,
        help_text='Additional notes from optometrist'
    )
    
    date_issued = models.DateField(
        help_text='Date when prescription was issued'
    )
    
    expiry_date = models.DateField(
        null=True,
        blank=True,
        help_text='Date when prescription expires (usually 2 years from issue)'
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text='Whether this prescription is currently active'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'prescriptions_prescription'
        ordering = ['-date_issued']
        unique_together = ['customer', 'date_issued']  # One prescription per customer per day
    
    def __str__(self):
        return f"Prescription for {self.customer.username} - {self.date_issued}"
    
    @property
    def is_expired(self):
        """Check if prescription has expired"""
        if self.expiry_date:
            from datetime import date
            return date.today() > self.expiry_date
        return False
    
    @property
    def left_eye_power(self):
        """Formatted left eye power for display"""
        if self.left_eye_cylinder == 0:
            return f"{self.left_eye_sphere:+.2f}"
        else:
            return f"{self.left_eye_sphere:+.2f} {self.left_eye_cylinder:+.2f} x {self.left_eye_axis or 0}"
    
    @property
    def right_eye_power(self):
        """Formatted right eye power for display"""
        if self.right_eye_cylinder == 0:
            return f"{self.right_eye_sphere:+.2f}"
        else:
            return f"{self.right_eye_sphere:+.2f} {self.right_eye_cylinder:+.2f} x {self.right_eye_axis or 0}"
    
    def save(self, *args, **kwargs):
        # Set expiry date if not provided (2 years from issue date)
        if not self.expiry_date and self.date_issued:
            from datetime import date
            from dateutil.relativedelta import relativedelta
            self.expiry_date = self.date_issued + relativedelta(years=2)
        
        super().save(*args, **kwargs)

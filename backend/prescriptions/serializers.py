# Reference: PROMPT.md → Prescription Module → Data Serialization.
# Purpose: Serialize and validate prescription data for API endpoints.
# Note: Link prescriptions to Customer and Optometrist using foreign key relationships.

from rest_framework import serializers
from .models import Prescription
from accounts.serializers import UserProfileSerializer

class PrescriptionListSerializer(serializers.ModelSerializer):
    """
    Serializer for prescription list view (minimal data)
    Reference: PROMPT.md → prescriptions_prescription with customer_id and optometrist_id
    """
    customer_name = serializers.SerializerMethodField()
    optometrist_name = serializers.SerializerMethodField()
    left_eye_power_display = serializers.CharField(source='left_eye_power', read_only=True)
    right_eye_power_display = serializers.CharField(source='right_eye_power', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Prescription
        fields = [
            'id', 'customer_name', 'optometrist_name',
            'left_eye_power_display', 'right_eye_power_display',
            'prescription_type', 'date_issued', 'expiry_date',
            'is_expired', 'is_active', 'created_at'
        ]
    
    def get_customer_name(self, obj):
        """Return customer display name"""
        return f"{obj.customer.first_name} {obj.customer.last_name}".strip() or obj.customer.username
    
    def get_optometrist_name(self, obj):
        """Return optometrist display name"""
        return f"{obj.optometrist.first_name} {obj.optometrist.last_name}".strip() or obj.optometrist.username

class PrescriptionDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed prescription view
    Reference: PROMPT.md → Prescription Model Fields with complete eye measurements
    """
    customer = UserProfileSerializer(read_only=True)
    optometrist = UserProfileSerializer(read_only=True)
    
    left_eye_power_display = serializers.CharField(source='left_eye_power', read_only=True)
    right_eye_power_display = serializers.CharField(source='right_eye_power', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Prescription
        fields = [
            'id', 'customer', 'optometrist',
            'left_eye_sphere', 'left_eye_cylinder', 'left_eye_axis',
            'right_eye_sphere', 'right_eye_cylinder', 'right_eye_axis',
            'left_eye_power_display', 'right_eye_power_display',
            'pupillary_distance', 'add_power', 'prescription_type',
            'additional_notes', 'date_issued', 'expiry_date',
            'is_expired', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class PrescriptionCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating prescriptions (optometrist use)
    Reference: PROMPT.md → React form for prescription entry (Optometrist dashboard)
    """
    class Meta:
        model = Prescription
        fields = [
            'customer', 'left_eye_sphere', 'left_eye_cylinder', 'left_eye_axis',
            'right_eye_sphere', 'right_eye_cylinder', 'right_eye_axis',
            'pupillary_distance', 'add_power', 'prescription_type',
            'additional_notes', 'date_issued', 'expiry_date'
        ]
    
    def validate_customer(self, value):
        """Validate customer role"""
        if value.role != 'customer':
            raise serializers.ValidationError("Prescriptions can only be assigned to customers")
        return value
    
    def validate(self, attrs):
        """Validate prescription data consistency"""
        # Validate axis values when cylinder is present
        left_cylinder = attrs.get('left_eye_cylinder', 0)
        right_cylinder = attrs.get('right_eye_cylinder', 0)
        left_axis = attrs.get('left_eye_axis')
        right_axis = attrs.get('right_eye_axis')
        
        if left_cylinder != 0 and not left_axis:
            raise serializers.ValidationError(
                "Left eye axis is required when cylinder power is specified"
            )
        
        if right_cylinder != 0 and not right_axis:
            raise serializers.ValidationError(
                "Right eye axis is required when cylinder power is specified"
            )
        
        # Validate add power for progressive prescriptions
        prescription_type = attrs.get('prescription_type')
        add_power = attrs.get('add_power')
        
        if prescription_type in ['progressive', 'bifocal'] and not add_power:
            raise serializers.ValidationError(
                "Add power is required for progressive and bifocal prescriptions"
            )
        
        return attrs
    
    def create(self, validated_data):
        """Create prescription with optometrist from request"""
        validated_data['optometrist'] = self.context['request'].user
        return super().create(validated_data)

class PrescriptionUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating prescriptions (optometrist only)
    Reference: PROMPT.md → Create/update/view operations
    """
    class Meta:
        model = Prescription
        fields = [
            'left_eye_sphere', 'left_eye_cylinder', 'left_eye_axis',
            'right_eye_sphere', 'right_eye_cylinder', 'right_eye_axis',
            'pupillary_distance', 'add_power', 'prescription_type',
            'additional_notes', 'date_issued', 'expiry_date', 'is_active'
        ]
    
    def validate(self, attrs):
        """Validate prescription updates"""
        # Use same validation as create
        return PrescriptionCreateSerializer.validate(self, attrs)

class CustomerPrescriptionSerializer(serializers.ModelSerializer):
    """
    Serializer for customer viewing their prescriptions
    Reference: PROMPT.md → Customers can view prescriptions in their profile
    """
    optometrist_name = serializers.SerializerMethodField()
    left_eye_power_display = serializers.CharField(source='left_eye_power', read_only=True)
    right_eye_power_display = serializers.CharField(source='right_eye_power', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    prescription_summary = serializers.SerializerMethodField()
    
    class Meta:
        model = Prescription
        fields = [
            'id', 'optometrist_name', 'left_eye_power_display',
            'right_eye_power_display', 'prescription_type',
            'prescription_summary', 'additional_notes',
            'date_issued', 'expiry_date', 'is_expired', 'is_active'
        ]
    
    def get_optometrist_name(self, obj):
        """Return optometrist display name"""
        return f"Dr. {obj.optometrist.first_name} {obj.optometrist.last_name}".strip()
    
    def get_prescription_summary(self, obj):
        """Return formatted prescription summary"""
        summary = {
            'left_eye': {
                'sphere': float(obj.left_eye_sphere),
                'cylinder': float(obj.left_eye_cylinder),
                'axis': obj.left_eye_axis,
                'display': obj.left_eye_power
            },
            'right_eye': {
                'sphere': float(obj.right_eye_sphere),
                'cylinder': float(obj.right_eye_cylinder),
                'axis': obj.right_eye_axis,
                'display': obj.right_eye_power
            }
        }
        
        if obj.pupillary_distance:
            summary['pupillary_distance'] = float(obj.pupillary_distance)
        
        if obj.add_power:
            summary['add_power'] = float(obj.add_power)
        
        return summary

class OptometristPrescriptionSerializer(serializers.ModelSerializer):
    """
    Serializer for optometrist viewing their issued prescriptions
    Reference: PROMPT.md → Optometrist sees prescriptions they issued
    """
    customer_name = serializers.SerializerMethodField()
    customer_contact = serializers.SerializerMethodField()
    left_eye_power_display = serializers.CharField(source='left_eye_power', read_only=True)
    right_eye_power_display = serializers.CharField(source='right_eye_power', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Prescription
        fields = [
            'id', 'customer_name', 'customer_contact',
            'left_eye_power_display', 'right_eye_power_display',
            'prescription_type', 'additional_notes',
            'date_issued', 'expiry_date', 'is_expired',
            'is_active', 'created_at', 'updated_at'
        ]
    
    def get_customer_name(self, obj):
        """Return customer display name"""
        return f"{obj.customer.first_name} {obj.customer.last_name}".strip() or obj.customer.username
    
    def get_customer_contact(self, obj):
        """Return customer contact information"""
        return {
            'email': obj.customer.email,
            'phone': obj.customer.phone
        }

class PrescriptionValidationSerializer(serializers.Serializer):
    """
    Serializer for prescription validation (checking if prescription is valid for order)
    Reference: PROMPT.md → Order linked to prescription if applicable
    """
    prescription_id = serializers.IntegerField()
    customer_id = serializers.IntegerField()
    
    def validate(self, attrs):
        """Validate prescription belongs to customer and is active"""
        try:
            prescription = Prescription.objects.get(
                id=attrs['prescription_id'],
                customer_id=attrs['customer_id'],
                is_active=True
            )
            
            if prescription.is_expired:
                raise serializers.ValidationError("Prescription has expired")
            
            attrs['prescription'] = prescription
            return attrs
            
        except Prescription.DoesNotExist:
            raise serializers.ValidationError("Invalid prescription for this customer")
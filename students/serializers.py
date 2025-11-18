from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Student, DailyMeal

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = "__all__"
        read_only_fields = ["user"]

class StudentSignupSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    student_name = serializers.CharField()
    et_number = serializers.CharField()
    student_phone_number = serializers.CharField()
    father_name = serializers.CharField()
    father_phone_number = serializers.CharField()
    student_email = serializers.EmailField()   # ⭐ ADD THIS

    fees_paid = serializers.DecimalField(max_digits=10, decimal_places=2)
    pending_fee = serializers.DecimalField(max_digits=10, decimal_places=2)
    utr_number = serializers.CharField(required=False, allow_blank=True)
    room_type = serializers.CharField()
    student_image = serializers.ImageField(required=False, allow_null=True)   # ⭐ ADD THIS


class StudentApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ["is_verified"]

class DailyMealSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyMeal
        fields = "__all__"
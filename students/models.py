from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    student_name = models.CharField(max_length=100)
    et_number = models.CharField(max_length=50, unique=True)
    student_phone_number = models.CharField(max_length=15)

    father_name = models.CharField(max_length=100)
    father_phone_number = models.CharField(max_length=15)
    student_email = models.EmailField(max_length=254, blank=True, null=True)

    fees_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    utr_number = models.CharField(max_length=100, null=True, blank=True)
    pending_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    room_type = models.CharField(max_length=50)

    # ⭐ NEW FIELD
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.student_name

class PasswordResetOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=15)
from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        "id", 
        "student_name", 
        "et_number",
        "student_phone_number", 
        "father_name", 
        "fees_paid", 
        "pending_fee",
        "room_type",
        "is_verified",
    )

    # Make verification editable directly from list view
    list_editable = ("is_verified",)

    # To search specific students
    search_fields = ("student_name", "et_number", "student_phone_number")

    # Filter on sidebar
    list_filter = ("is_verified", "room_type")

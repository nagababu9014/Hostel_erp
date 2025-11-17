from django.contrib import admin
from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):

    list_display = (
        "student_name",        # make this first (NOT id)
        "id",
        "et_number",
        "student_email",
        "student_phone_number",
        "father_name",
        "fees_paid",
        "pending_fee",
        "room_type",
        "is_verified",
    )

    list_editable = ("is_verified",)

    fields = (
        "student_name",
        "et_number",
        "student_email",
        "student_phone_number",
        "father_name",
        "father_phone_number",
        "fees_paid",
        "pending_fee",
        "utr_number",
        "room_type",
        "is_verified",
    )

    search_fields = ("student_name", "et_number", "student_phone_number")
    list_filter = ("is_verified", "room_type")

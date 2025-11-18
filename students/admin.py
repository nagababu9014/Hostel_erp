from django.contrib import admin
from django.utils.html import format_html
from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):

    list_display = (
        "student_name",
        "id",
        "et_number",
        "student_email",
        "student_phone_number",
        "father_name",
        "fees_paid",
        "pending_fee",
        "room_type",
        "is_verified",
        "image_preview",   # ⭐ Add preview column
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
        "student_image",         # ⭐ Show upload field in admin page
        "image_preview",         # ⭐ Show preview inside edit page
    )

    readonly_fields = ("image_preview",)   # ⭐ Prevent editing preview

    search_fields = ("student_name", "et_number", "student_phone_number")
    list_filter = ("is_verified", "room_type")

    # ⭐ Function to show preview
    def image_preview(self, obj):
        if obj.student_image:
            return format_html(
                '<img src="{}" width="70" height="70" style="border-radius:5px; object-fit:cover;" />',
                obj.student_image.url
            )
        return "No Image"

    image_preview.short_description = "Photo"


from django.contrib import admin
from .models import StaffRole

@admin.register(StaffRole)
class StaffRoleAdmin(admin.ModelAdmin):
    list_display = ("user", "role")
    list_filter = ("role",)
    search_fields = ("user__username",)

from django.urls import path
from .api_views import (
    signup_api, verified_login,
    student_dashboard, approve_student, test_api
)

urlpatterns = [
    path("signup/", signup_api),
    path("login/", verified_login),
    path("dashboard/", student_dashboard),
    path("admin/approve/<int:student_id>/", approve_student),
    path("test/", test_api),

]

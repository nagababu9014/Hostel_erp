from django.urls import path
from .api_views import (
    signup_api, verified_login,
    student_dashboard, approve_student, test_api , forgot_password, reset_password,OfficeDashboardAPI,
    OfficeEditStudentAPI,
    OfficeApproveStudentAPI,
    OfficeDeleteStudentAPI,
)

urlpatterns = [
    path("signup/", signup_api),
    path("login/", verified_login),
    path("dashboard/", student_dashboard),
    path("admin/approve/<int:student_id>/", approve_student),
    path("test/", test_api),
    path("forgot-password/", forgot_password),
    path("reset-password/", reset_password),


    path("office/dashboard/", OfficeDashboardAPI.as_view()),

    path("office/student/edit/<int:student_id>/", OfficeEditStudentAPI.as_view()),
    path("office/student/approve/<int:student_id>/", OfficeApproveStudentAPI.as_view()),
    path("office/student/delete/<int:student_id>/", OfficeDeleteStudentAPI.as_view()),
]

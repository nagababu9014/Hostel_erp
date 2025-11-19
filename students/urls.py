from django.urls import path
from .api_views import (
    signup_api, verified_login,
    student_dashboard, approve_student, test_api , forgot_password, reset_password,OfficeDashboardAPI,
    OfficeEditStudentAPI,
    OfficeApproveStudentAPI,
    OfficeDeleteStudentAPI,
    GenerateDailyQR,
    StudentQRView,
    ScanQRAPIView,
    UpdateMealDecision,
    ScanMealAPIView,
    KitchenCountAPI,
)

urlpatterns = [
    path("signup/", signup_api),
    path("login/", verified_login),
    path("dashboard/", student_dashboard),
    path("test/", test_api),
    path("forgot-password/", forgot_password),
    path("reset-password/", reset_password),


    path("office/dashboard/", OfficeDashboardAPI.as_view()),
    path("office/student/edit/<int:student_id>/", OfficeEditStudentAPI.as_view()),
    path("office/student/approve/<int:student_id>/", OfficeApproveStudentAPI.as_view()),
    path("office/student/delete/<int:student_id>/", OfficeDeleteStudentAPI.as_view()),


    path("generate-daily-qr/", GenerateDailyQR.as_view()),
    path("student/qr/", StudentQRView.as_view()),
    path("scan/qr/", ScanQRAPIView.as_view()),
    path("meal/decision/", UpdateMealDecision.as_view()),
    path("meal/scan/", ScanMealAPIView.as_view()),
    path("kitchen/count/", KitchenCountAPI.as_view()),
]

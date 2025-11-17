from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    StudentSignupSerializer,
    StudentSerializer,
    StudentApprovalSerializer,
)

from .models import Student , PasswordResetOTP
import random
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
# SIGNUP API (stored as pending)

@api_view(["POST"])
def signup_api(request):
    serializer = StudentSignupSerializer(data=request.data)

    if serializer.is_valid():
        data = serializer.validated_data

        # create user
        user = User.objects.create_user(
            username=data["username"],
            password=data["password"],
            email=data["student_email"]     # ⭐ SAVE EMAIL HERE

        )

        # create student profile
        Student.objects.create(
            user=user,
            student_name=data["student_name"],
            et_number=data["et_number"],
            student_phone_number=data["student_phone_number"],
            father_name=data["father_name"],
            father_phone_number=data["father_phone_number"],
            fees_paid=data["fees_paid"],
            pending_fee=data["pending_fee"],
            utr_number=data["utr_number"],
            room_type=data["room_type"],
            is_verified=False   # ⭐ pending approval
        )

        return Response({"message": "Signup successful! Waiting for admin approval."})

    return Response(serializer.errors, status=400)

@api_view(["POST"])
def forgot_password(request):
    username = request.data.get("username")

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

    # Automatically fetch registered email
    email = user.student.student_email

    if not email:
        return Response({"error": "No email linked with this account"}, status=400)

    # Generate 6-digit OTP
    otp = str(random.randint(100000, 999999))

    # Save OTP in DB
    PasswordResetOTP.objects.create(user=user, otp=otp)

    # Send OTP email
    send_mail(
        subject="Hostel ERP - Password Reset OTP",
        message=f"Your OTP to reset password is: {otp}\n\nValid for 15 minutes.",
        from_email="ballanagababu29@gmail.com",
        recipient_list=[email],
        fail_silently=False,
    )

    return Response({"message": "OTP sent to your registered email"})

@api_view(["POST"])
def reset_password(request):
    username = request.data.get("username")
    otp = request.data.get("otp")
    new_password = request.data.get("new_password")

    # get user
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

    # get OTP entry
    try:
        otp_obj = PasswordResetOTP.objects.filter(user=user, otp=otp).latest('created_at')
    except PasswordResetOTP.DoesNotExist:
        return Response({"error": "Invalid OTP"}, status=400)

    # check expiration
    if otp_obj.is_expired():
        return Response({"error": "OTP expired"}, status=400)

    # update password
    user.password = make_password(new_password)
    user.save()

    # clear otp history
    PasswordResetOTP.objects.filter(user=user).delete()

    return Response({"message": "Password reset successful"})


# ADMIN APPROVE API
@api_view(["PATCH"])
@permission_classes([IsAdminUser])
def approve_student(request, student_id):
    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        return Response({"error": "Student not found"}, status=404)

    serializer = StudentApprovalSerializer(student, data={"is_verified": True}, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Student approved successfully"})
    
    return Response(serializer.errors, status=400)

@api_view(["POST"])
def verified_login(request):
    username = request.data.get("username")
    password = request.data.get("password")

    user = authenticate(username=username, password=password)

    if not user:
        return Response({"error": "Invalid username or password"}, status=400)

    # ⭐ If user is admin (superuser or staff)
    if user.is_superuser or user.is_staff:
        refresh = RefreshToken.for_user(user)
        return Response({
            "message": "Admin login successful",
            "role": "admin",
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        })

    # ⭐ Otherwise it is a student login — check student profile
    try:
        student = Student.objects.get(user=user)
    except Student.DoesNotExist:
        return Response({"error": "Student profile not found"}, status=404)

    # ⭐ Student must be verified by admin
    if not student.is_verified:
        return Response({"error": "Your account is not yet approved by admin"}, status=403)

    # ⭐ Student login success
    refresh = RefreshToken.for_user(user)
    return Response({
        "message": "Student login successful",
        "role": "student",
        "access": str(refresh.access_token),
        "refresh": str(refresh)
    })

# STUDENT DASHBOARD API
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def student_dashboard(request):
    student = Student.objects.get(user=request.user)
    serializer = StudentSerializer(student)
    return Response(serializer.data)


from django.http import JsonResponse

def test_api(request):
    return JsonResponse({"message": "API is working!"})

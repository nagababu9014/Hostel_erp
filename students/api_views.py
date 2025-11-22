from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    StudentSignupSerializer,
    StudentSerializer,
    StudentApprovalSerializer,
)

from .models import Student , PasswordResetOTP,StaffRole
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
            student_email=data["student_email"],   # ⭐ ADD THIS

            fees_paid=data["fees_paid"],
            pending_fee=data["pending_fee"],
            utr_number=data["utr_number"],
            room_type=data["room_type"],
            is_verified=False ,  # ⭐ pending approval
            student_image=data.get("student_image", None)   # ⭐ SAVE IMAGE HERE

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

    refresh = RefreshToken.for_user(user)

    # ✔ 1. Admin login
    if user.is_superuser or user.is_staff:
        return Response({
            "message": "Admin login successful",
            "role": "admin",
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        })

    # ✔ 2. Check StaffRole (office, warden, accounts, kitchen)
    try:
        staff_role = StaffRole.objects.get(user=user)
        return Response({
            "message": "Staff login successful",
            "role": staff_role.role,
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        })
    except StaffRole.DoesNotExist:
        pass  # Continue to student check

    # ✔ 3. Student login
    try:
        student = Student.objects.get(user=user)
    except Student.DoesNotExist:
        return Response({"error": "Student profile not found"}, status=404)

    # student must be approved
    if not student.is_verified:
        return Response({"error": "Your account is not yet approved by admin"}, status=403)

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



from rest_framework.views import APIView
from .decorators import role_required
class OfficeDashboardAPI(APIView):

    @role_required(['owner', 'office'])
    def get(self, request):

        all_students = Student.objects.all().values(
            "id", "student_name", "et_number", "student_phone_number","student_image",
            "father_name", "father_phone_number",
            "student_email", "room_type", "is_verified"
        )

        pending_students = Student.objects.filter(is_verified=False).values(
            "id", "student_name", "et_number", "student_phone_number","student_image"
        )

        return Response({
            "students": list(all_students),
            "pending_verification": list(pending_students)
        })

class OfficeEditStudentAPI(APIView):

    @role_required(['owner', 'office'])
    def put(self, request, student_id):
        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return Response({"error": "Student not found"}, status=404)

        allowed_fields = [
            "student_name",
            "student_phone_number",
            "father_name",
            "father_phone_number",
            "student_email",
            "room_type",
        ]

        for field in allowed_fields:
            if field in request.data:
                setattr(student, field, request.data[field])

        student.save()
        return Response({"message": "Student updated successfully"})


class OfficeApproveStudentAPI(APIView):

    @role_required(['owner', 'office'])
    def post(self, request, student_id):
        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return Response({"error": "Student not found"}, status=404)

        student.is_verified = True
        student.save()

        return Response({"message": "Student approved successfully"})

class OfficeDeleteStudentAPI(APIView):

    @role_required(['owner', 'office'])
    def delete(self, request, student_id):
        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return Response({"error": "Student not found"}, status=404)

        student.delete()
        return Response({"message": "Student deleted successfully"})
    

import uuid
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import DailyMeal, Student
from .decorators import role_required
from .serializers import DailyMealSerializer, StudentSerializer
from django.conf import settings
from datetime import time as dtime

# Helper to get meal time ranges from settings or fallback defaults
MEAL_RANGES = getattr(settings, "MEAL_TIME_RANGES", {
    "breakfast": {"start": dtime(7, 0), "end": dtime(10, 30)},
    "lunch": {"start": dtime(12, 0), "end": dtime(15, 0)},
    "dinner": {"start": dtime(19, 0), "end": dtime(21, 0)},
})

def is_within_meal_window(meal_type, now=None):
    if now is None:
        now = timezone.localtime().time()
    rng = MEAL_RANGES.get(meal_type)
    if not rng:
        return False
    start = rng["start"]
    end = rng["end"]
    # simple inclusive check (works if start < end)
    return start <= now <= end

# -------------------------
# STEP: Generate Daily QRs
# -------------------------
class GenerateDailyQR(APIView):
    @role_required(['owner', 'office','warden'])
    def post(self, request):
        today = timezone.now().date()
        students = Student.objects.filter(is_verified=True)
        created = 0
        for student in students:
            token = str(uuid.uuid4())
            obj, _ = DailyMeal.objects.update_or_create(
                student=student,
                date=today,
                defaults={"qr_token": token}
            )
            created += 1
        return Response({"message": f"Daily QRs generated for {created} students"})
    
# aUTO QR
from rest_framework.permissions import AllowAny

class AutoGenerateDailyQR(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        # simple security key
        if request.GET.get("key") != "HOSTEL_SECRET_2025":
            return Response({"error": "Unauthorized"}, status=403)

        today = timezone.now().date()

        # Prevent duplicate generation
        if DailyMeal.objects.filter(date=today).exists():
            return Response({"message": "QR already generated today"})

        students = Student.objects.filter(is_verified=True)
        created = 0

        for student in students:
            DailyMeal.objects.update_or_create(
                student=student,
                date=today,
                defaults={"qr_token": str(uuid.uuid4())}
            )
            created += 1

        return Response({"message": f"AUTO Daily QRs generated for {created} students"})

# -------------------------
# STEP: Student view own QR
# -------------------------
class StudentQRView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            student = Student.objects.get(user=request.user)
        except Student.DoesNotExist:
            return Response({"error":"Student profile not found"}, status=404)

        today = timezone.now().date()
        try:
            meal = DailyMeal.objects.get(student=student, date=today)
        except DailyMeal.DoesNotExist:
            return Response({"error":"No QR generated for today"}, status=404)

        return Response({
            "qr_token": meal.qr_token,
            "date": str(meal.date)
        })

# -------------------------
# STEP: Scan QR (show status + image)
# -------------------------
class ScanQRAPIView(APIView):
    @role_required(['warden', 'owner', 'office'])  # optional: add office
    def post(self, request):
        token = request.data.get("qr_token")

        if not token:
            return Response({"error": "qr_token required"}, status=400)

        try:
            meal = DailyMeal.objects.get(
                qr_token=token,
                date=timezone.now().date()  # must be today's QR
            )
        except DailyMeal.DoesNotExist:
            return Response({"error": "Invalid or expired QR"}, status=404)

        student = meal.student

        return Response({
            "student_id": student.id,
            "student_name": student.student_name,
            "et_number": student.et_number,
            "student_image": student.student_image.url if student.student_image else None,

            "breakfast": meal.breakfast,
            "lunch": meal.lunch,
            "dinner": meal.dinner,

            "breakfast_scanned": meal.breakfast_scanned,
            "lunch_scanned": meal.lunch_scanned,
            "dinner_scanned": meal.dinner_scanned,
        })

# -------------------------
# STEP: Breakfast-time decision (set lunch/dinner yes/no)
# Only usable during breakfast window
# -------------------------
class MealActionAPIView(APIView):
    @role_required(['warden', 'owner'])
    def post(self, request):
        qr = request.data.get("qr_token")
        action = request.data.get("action")  # breakfast/lunch/dinner

        if action not in ("breakfast", "lunch", "dinner"):
            return Response({"error": "action must be breakfast/lunch/dinner"}, status=400)

        try:
            meal = DailyMeal.objects.get(qr_token=qr, date=timezone.now().date())
        except DailyMeal.DoesNotExist:
            return Response({"error": "Invalid QR"}, status=404)

        # CURRENT TIME WINDOW
        now_window = None
        for m in ("breakfast","lunch","dinner"):
            if is_within_meal_window(m):
                now_window = m
                break

        # --------------------------------------------------------
        # CASE 1: BREAKFAST BUTTON
        # --------------------------------------------------------
        if action == "breakfast":
            if meal.breakfast_scanned:
                return Response({"error": "Breakfast already scanned"}, status=400)

            meal.breakfast_scanned = True
            if meal.breakfast is None:
                meal.breakfast = True

            meal.save()
            return Response({"message": "Breakfast marked done"})

        # --------------------------------------------------------
        # CASE 2: LUNCH BUTTON
        # --------------------------------------------------------
        if action == "lunch":
            # Morning time (breakfast window) → decision
            if now_window == "breakfast":
                meal.lunch = False
                meal.save()
                return Response({"message": "Lunch opted NO (count reduced)"})

            # Afternoon time → scan
            if now_window == "lunch":
                if meal.lunch is False:
                    return Response({"error": "Student opted NO for lunch"}, status=400)
                if meal.lunch_scanned:
                    return Response({"error": "Lunch already scanned"}, status=400)

                meal.lunch_scanned = True
                if meal.lunch is None:
                    meal.lunch = True
                meal.save()
                return Response({"message": "Lunch scan completed"})

            return Response({"error": "Cannot update lunch at this time"}, status=403)

        # --------------------------------------------------------
        # CASE 3: DINNER BUTTON
        # --------------------------------------------------------
        if action == "dinner":
            # Morning time → dinner decision
            if now_window == "breakfast":
                meal.dinner = False
                meal.save()
                return Response({"message": "Dinner opted NO (count reduced)"})

            # Evening → scan dinner
            if now_window == "dinner":
                if meal.dinner is False:
                    return Response({"error": "Student opted NO for dinner"}, status=400)
                if meal.dinner_scanned:
                    return Response({"error": "Dinner already scanned"}, status=400)

                meal.dinner_scanned = True
                if meal.dinner is None:
                    meal.dinner = True
                meal.save()
                return Response({"message": "Dinner scan completed"})

            return Response({"error": "Cannot update dinner at this time"}, status=403)

# -------------------------
# STEP: Kitchen counts API
# -------------------------
class KitchenCountAPI(APIView):
    @role_required(['kitchen','owner'])
    def get(self, request):
        today = timezone.now().date()
        # breakfast: count who scanned breakfast (present)
        breakfast_count = DailyMeal.objects.filter(date=today, breakfast_scanned=True).count()
        # lunch: count who opted True (or None treated as True) and are verified students
        lunch_count = DailyMeal.objects.filter(date=today).exclude(lunch=False).count()
        # dinner similar
        dinner_count = DailyMeal.objects.filter(date=today).exclude(dinner=False).count()

        return Response({
            "breakfast_count": breakfast_count,
            "lunch_count": lunch_count,
            "dinner_count": dinner_count
        })

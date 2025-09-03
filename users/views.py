from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from django.middleware.csrf import get_token
from django.contrib.auth.models import User

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema, OpenApiParameter

from .serializers import LoginSerializer, SignupSerializer, VerifySerializer

from django.core.mail import send_mail
from .models import EmailOTP

from django.views.decorators.csrf import csrf_exempt
from drf_yasg.utils import swagger_auto_schema

@extend_schema(
    description="Get a CSRF cookie and token. Call this first from browsers/Swagger.",
    responses={"200": {"type": "object", "properties": {"csrfToken": {"type": "string"}}}},
)

@api_view(["GET"])
@permission_classes([AllowAny])
@ensure_csrf_cookie  # sets 'csrftoken' cookie
def csrf_view(request):
    """
    Returns the CSRF token and sets the csrftoken cookie.
    DRF's SessionAuthentication expects X-CSRFToken header for unsafe methods.
    """
    token = get_token(request)
    return Response({"csrfToken": token})


@extend_schema(
    description="Log in with username & password. Sets 'sessionid' cookie.",
    request=LoginSerializer,
    responses={200: {"type": "object", "properties": {"detail": {"type": "string"}}}},
    parameters=[
        OpenApiParameter(name="X-CSRFToken", location=OpenApiParameter.HEADER, required=True, type=str,
                         description="CSRF token from /api/csrf/"),
    ],
)
@api_view(["POST"])
@permission_classes([AllowAny])          # allow anyone to attempt login
@authentication_classes([SessionAuthentication])
@csrf_protect                              # require CSRF header
# @csrf_exempt                            #swagger does not send cookie, so view use this
def login_view(request):

    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    username = serializer.validated_data["username"]
    password = serializer.validated_data["password"]

    user = authenticate(request, username=username, password=password)
    if not user:
        return Response({"detail": "Invalid credentials."}, status=status.HTTP_400_BAD_REQUEST)

    login(request, user)  # creates the session & sets 'sessionid' cookie
    return Response({"detail": "Logged in."}, status=status.HTTP_200_OK)


@extend_schema(
    description="Log out and clear session.",
    responses={200: {"type": "object", "properties": {"detail": {"type": "string"}}}},
    parameters=[
        OpenApiParameter(name="X-CSRFToken", location=OpenApiParameter.HEADER, required=True, type=str,
                         description="CSRF token from /api/csrf/"),
    ],
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])    # must be logged in to log out
@authentication_classes([SessionAuthentication])
@csrf_protect
def logout_view(request):
    logout(request)
    return Response({"detail": "Logged out."})


@extend_schema(
    description="Who am I? Returns the authenticated user.",
    responses={200: {"type": "object",
                     "properties": {"username": {"type": "string"}, "is_authenticated": {"type": "boolean"}}}},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])    # must be logged in
def me_view(request):
    user = request.user
    return Response({"username": user.username, "is_authenticated": user.is_authenticated})


# @csrf_exempt  
# @extend_schema(
#     description="Register a new user.",
#     request=SignupSerializer,
#     responses={201: {"type": "object", "properties": {"detail": {"type": "string"}}}}
# )
# @api_view(['POST'])
# def signup(request):
#     serializer = SignupSerializer(data=request.data)
#     if serializer.is_valid():
#         username = serializer.validated_data['username']
#         password = serializer.validated_data['password']
#         email = serializer.validated_data.get('email', '')

#         if User.objects.filter(username=username).exists():
#             return Response({"error": "Username already exists"}, status=400)

#         user = User.objects.create_user(username=username, password=password, email=email)
#         user.save()
#         return Response({"detail": "User created successfully"}, status=201)
#     else:
#         return Response(serializer.errors, status=400)

@csrf_exempt
@extend_schema(
    description="Register a new user and send OTP to email.",
    request=SignupSerializer,
    responses={201: {"type": "object", "properties": {"detail": {"type": "string"}}}}
)
@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    serializer = SignupSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        email = serializer.validated_data.get('email', '')

        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already exists"}, status=400)

        user = User.objects.create_user(username=username, password=password, email=email, is_active=False)
        user.save()

        otp_obj, _ = EmailOTP.objects.get_or_create(user=user)
        otp = otp_obj.generate_otp()


        send_mail(
            subject="Your Verification Code",
            message=f"Hi {username},\n\nYour OTP is: {otp}\n\nUse this to verify your account.",
            from_email=None, 
            recipient_list=[email],
        )

        return Response({"detail": "User created successfully. Please verify your email with OTP."}, status=201)
    else:
        return Response(serializer.errors, status=400)
    

@extend_schema(
    description="Verify OTP to activate account.",
    request=VerifySerializer,
    responses={200: {"type": "object", "properties": {"detail": {"type": "string"}}}}
)
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_email(request):
    serializer = VerifySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    email = serializer.validated_data['email']
    otp = serializer.validated_data['otp']

    try:
        user = User.objects.get(email=email)
        otp_obj = user.email_otp
    except (User.DoesNotExist, EmailOTP.DoesNotExist):
        return Response({"error": "Invalid email or OTP"}, status=400)

    if otp_obj.verified:
        return Response({"detail": "Email already verified"}, status=200)

    if otp_obj.otp == otp:
        otp_obj.verified = True
        otp_obj.save()
        user.is_active = True
        user.save()
        return Response({"detail": "Email verified successfully. You can now login."}, status=200)
    else:
        return Response({"error": "Invalid OTP"}, status=400)
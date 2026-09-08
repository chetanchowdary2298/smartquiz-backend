
import os
import requests

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes
)
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from django.utils.http import (
    urlsafe_base64_decode,
    urlsafe_base64_encode
)
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

from .models import Question
from .models import QuizScore, Subject

import re


# ============================================================
# BREVO EMAIL HELPER
# ============================================================

def send_brevo_email(to_email, subject, text_content, html_content):
    """
    Sends an email through Brevo's HTTPS API.
    This avoids Railway's SMTP restriction.
    """

    api_key = os.environ.get("BREVO_API_KEY")

    if not api_key:
        raise Exception(
            "BREVO_API_KEY is not configured on the server."
        )

    payload = {
        "sender": {
            "name": "SmartQuiz Portal",
            "email": "770superuser770@gmail.com"
        },
        "to": [
            {
                "email": to_email
            }
        ],
        "subject": subject,
        "textContent": text_content,
        "htmlContent": html_content
    }

    headers = {
        "accept": "application/json",
        "api-key": api_key,
        "content-type": "application/json"
    }

    response = requests.post(
        "https://api.brevo.com/v3/smtp/email",
        json=payload,
        headers=headers,
        timeout=15
    )

    if response.status_code not in [200, 201, 202]:
        try:
            error_data = response.json()
        except Exception:
            error_data = response.text

        raise Exception(
            f"Brevo email error ({response.status_code}): {error_data}"
        )

    return response.json()


# ============================================================
# REGISTER
# ============================================================

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):

    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')

    if not username or not email or not password:
        return Response(
            {'error': 'All fields are required.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if User.objects.filter(username=username).exists():
        return Response(
            {'error': 'Username already taken.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )

    refresh = RefreshToken.for_user(user)

    return Response(
        {
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            },
            'token': str(refresh.access_token)
        },
        status=status.HTTP_201_CREATED
    )


# ============================================================
# LOGIN
# ============================================================

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):

    username_or_email = request.data.get('username')
    password = request.data.get('password')

    if not username_or_email or not password:
        return Response(
            {
                'error':
                'Username/email and password are required.'
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # First try normal username login
    user = authenticate(
        username=username_or_email,
        password=password
    )

    # If username login fails, try registered email
    if user is None:
        user_by_email = User.objects.filter(
            email__iexact=username_or_email
        ).first()

        if user_by_email:
            user = authenticate(
                username=user_by_email.username,
                password=password
            )

    if user is not None:

        refresh = RefreshToken.for_user(user)

        return Response({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            },
            'token': str(refresh.access_token)
        })

    return Response(
        {'error': 'Invalid credentials.'},
        status=status.HTTP_401_UNAUTHORIZED
    )


# ============================================================
# PASSWORD RESET REQUEST
# ============================================================

class PasswordResetApiView(APIView):

    @permission_classes([AllowAny])
    def post(self, request):

        email = request.data.get('email')

        if not email:
            return Response(
                {"error": "Email address is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Find the user using the registered email
        user = User.objects.filter(email=email).first()

        if user:

            try:

                # ------------------------------------------------
                # Generate secure UID and password reset token
                # ------------------------------------------------

                uid = urlsafe_base64_encode(
                    force_bytes(user.pk)
                )

                token = default_token_generator.make_token(user)

                # ------------------------------------------------
                # Get frontend URL from Railway environment
                # ------------------------------------------------

                frontend_url = os.environ.get(
                    "FRONTEND_URL",
                    "http://localhost:5173"
                ).rstrip("/")

                # ------------------------------------------------
                # Create password reset link
                # ------------------------------------------------

                reset_link = (
                    f"{frontend_url}/reset-password"
                    f"?uid={uid}&token={token}"
                )

                # ------------------------------------------------
                # Email subject
                # ------------------------------------------------

                email_subject = "Reset Your SmartQuiz Password"

                # ------------------------------------------------
                # Plain-text email
                # ------------------------------------------------

                email_body = (
                    f"Hello {user.username},\n\n"
                    f"You requested a password reset for your "
                    f"SmartQuiz student account.\n\n"
                    f"Please use the link below to reset your password:\n\n"
                    f"{reset_link}\n\n"
                    f"This link is specific to your account.\n"
                    f"If you did not request a password reset, "
                    f"please safely ignore this email.\n\n"
                    f"Regards,\n"
                    f"SmartQuiz Portal"
                )

                # ------------------------------------------------
                # HTML email
                # ------------------------------------------------

                html_body = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <title>Reset Your SmartQuiz Password</title>
                </head>

                <body style="
                    margin: 0;
                    padding: 0;
                    background-color: #f5f7f7;
                    font-family: Arial, sans-serif;
                ">

                    <div style="
                        max-width: 600px;
                        margin: 40px auto;
                        background: white;
                        padding: 30px;
                        border-radius: 12px;
                    ">

                        <h2 style="margin-top: 0;">
                            Reset Your SmartQuiz Password
                        </h2>

                        <p>
                            Hello <strong>{user.username}</strong>,
                        </p>

                        <p>
                            You requested a password reset for your
                            SmartQuiz student account.
                        </p>

                        <p>
                            Click the button below to create a new password:
                        </p>

                        <p style="margin: 30px 0;">
                            <a
                                href="{reset_link}"
                                style="
                                    display: inline-block;
                                    padding: 12px 22px;
                                    background-color: #5D7971;
                                    color: white;
                                    text-decoration: none;
                                    border-radius: 6px;
                                    font-weight: bold;
                                "
                            >
                                Reset Password
                            </a>
                        </p>

                        <p>
                            If the button does not work, use this link:
                        </p>

                        <p style="
                            word-break: break-all;
                            color: #5D7971;
                        ">
                            {reset_link}
                        </p>

                        <p>
                            If you did not request a password reset,
                            please safely ignore this email.
                        </p>

                        <p>
                            Regards,<br>
                            <strong>SmartQuiz Portal</strong>
                        </p>

                    </div>

                </body>
                </html>
                """

                # ------------------------------------------------
                # Send through Brevo HTTPS API
                # ------------------------------------------------

                send_brevo_email(
                    to_email=user.email,
                    subject=email_subject,
                    text_content=email_body,
                    html_content=html_body
                )

            except Exception as e:

                print(
                    "--- BREVO PASSWORD RESET EMAIL FAILURE ---:",
                    str(e)
                )

                return Response(
                    {
                        "error":
                        f"Internal mail delivery issue: {str(e)}"
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        # Do not reveal whether an email exists in the database
        return Response(
            {
                "message":
                "Password reset email sent if account exists."
            },
            status=status.HTTP_200_OK
        )


# ============================================================
# PASSWORD RESET CONFIRMATION
# ============================================================

class PasswordResetConfirmApiView(APIView):

    @permission_classes([AllowAny])
    def post(self, request, uidb64, token):

        try:

            # Sanitize encoded values
            clean_uidb64 = uidb64.replace('/', '')
            clean_token = token.replace('/', '')

            uid = urlsafe_base64_decode(
                clean_uidb64
            ).decode()

            user = User.objects.get(pk=uid)

        except (
            TypeError,
            ValueError,
            OverflowError,
            User.DoesNotExist
        ):

            user = None

        if (
            user is not None
            and default_token_generator.check_token(
                user,
                clean_token
            )
        ):

            new_password = request.data.get('password')

            user.set_password(new_password)
            user.save()

            return Response(
                {"message": "Password reset successful"},
                status=status.HTTP_200_OK
            )

        return Response(
            {"error": "Invalid token or user ID"},
            status=status.HTTP_400_BAD_REQUEST
        )


# ============================================================
# GET SUBJECTS
# ============================================================

@api_view(['GET'])
@permission_classes([AllowAny])
def get_subjects(request):

    subjects = Subject.objects.all()

    from .serializers import SubjectSerializer

    serializer = SubjectSerializer(
        subjects,
        many=True
    )

    return Response(serializer.data)


# ============================================================
# GET QUESTIONS BY SUBJECT
# ============================================================

@api_view(['GET'])
@permission_classes([AllowAny])
def get_questions_by_subject(request, subject_id):

    try:

        questions = Question.objects.filter(
            subject_id=subject_id
        )

        from .serializers import QuestionSerializer

        serializer = QuestionSerializer(
            questions,
            many=True
        )

        return Response(serializer.data)

    except Exception as e:

        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


# ============================================================
# QUESTION LIST
# ============================================================

class QuestionListView(APIView):

    def get(self, request):

        language_name = request.query_params.get(
            'language',
            ''
        ).strip()

        topic_name = request.query_params.get(
            'topic',
            ''
        ).strip()

        limit = request.query_params.get(
            'limit',
            10
        )

        if language_name.lower() == 'cpp':
            language_name = 'C++'

        try:
            limit = int(limit)

        except (ValueError, TypeError):
            limit = 10

        # Maximum 30 questions
        limit = max(1, min(limit, 30))

        queryset = Question.objects.filter(
            subject__name__iexact=language_name
        )

        if topic_name:

            queryset = queryset.filter(
                topic__iexact=topic_name
            )

        questions = queryset.order_by('?')[:limit]

        data = []

        for q in questions:

            cleaned_text = q.text

            if ']' in cleaned_text:

                cleaned_text = cleaned_text.split(
                    ']',
                    1
                )[-1].strip()

            correct_ans_letter = (
                q.correct_answer.upper().strip()
            )

            data.append({
                "id": q.id,
                "text": cleaned_text,
                "options": [

                    {
                        "text": q.option_a,
                        "is_correct": correct_ans_letter == 'A'
                    },

                    {
                        "text": q.option_b,
                        "is_correct": correct_ans_letter == 'B'
                    },

                    {
                        "text": q.option_c,
                        "is_correct": correct_ans_letter == 'C'
                    },

                    {
                        "text": q.option_d,
                        "is_correct": correct_ans_letter == 'D'
                    }

                ]
            })

        return Response(
            data,
            status=status.HTTP_200_OK
        )


# ============================================================
# SAVE QUIZ SCORE
# ============================================================

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def save_quiz_score(request):

    try:

        language = request.data.get(
            'language',
            ''
        ).strip()

        score_val = request.data.get('score')
        total_q = request.data.get('total_questions')

        if language.lower() in [
            'cpp',
            'cplusplus'
        ]:

            language = 'C++'

        elif language.lower() == 'java':

            language = 'Java'

        subject = Subject.objects.filter(
            name__iexact=language
        ).first()

        if not subject:

            return Response(
                {
                    "error":
                    f"Subject '{language}' not found in database"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        user = request.user

        quiz_score = QuizScore.objects.create(
            user=user,
            subject=subject,
            score=int(score_val),
            total_questions=int(total_q)
        )

        return Response(
            {
                "message": "Score saved successfully!",
                "id": quiz_score.id
            },
            status=status.HTTP_201_CREATED
        )

    except Exception as e:

        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ============================================================
# SUPPORT EMAIL
# ============================================================

@api_view(['POST'])
@permission_classes([AllowAny])
def send_support_email(request):

    name = request.data.get('name')
    user_email = request.data.get('email')
    message = request.data.get('message')

    if not name or not user_email or not message:

        return Response(
            {"error": "All fields are required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:

        email_body = (
            f"New support inquiry from SmartQuiz Portal:\n\n"
            f"User's Name: {name}\n"
            f"User's Email: {user_email}\n\n"
            f"Message:\n{message}"
        )

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>SmartQuiz Support Request</title>
        </head>

        <body style="
            font-family: Arial, sans-serif;
            line-height: 1.6;
        ">

            <h2>SmartQuiz Support Request</h2>

            <p>
                <strong>User's Name:</strong> {name}
            </p>

            <p>
                <strong>User's Email:</strong> {user_email}
            </p>

            <hr>

            <p>
                <strong>Message:</strong>
            </p>

            <p>
                {message}
            </p>

        </body>
        </html>
        """

        send_brevo_email(
            to_email="770superuser770@gmail.com",
            subject=f"SmartQuiz Support Request - {name}",
            text_content=email_body,
            html_content=html_body
        )

        return Response(
            {"message": "Support message sent successfully!"},
            status=status.HTTP_200_OK
        )

    except Exception as e:

        print(
            "--- BREVO SUPPORT EMAIL FAILURE ---:",
            str(e)
        )

        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


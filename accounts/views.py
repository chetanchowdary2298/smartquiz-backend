import os

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
from django.contrib.auth.forms import PasswordResetForm
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string

from .models import Question
from .models import QuizScore, Subject

import re


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


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(
        username=username,
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


class PasswordResetApiView(APIView):

    @permission_classes([AllowAny])
    def post(self, request):

        email = request.data.get('email')

        if not email:
            return Response(
                {"error": "Email address is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Find the user matching the email address
        user = User.objects.filter(email=email).first()

        if user:
            try:
                # Generate secure UID and token
                uid = urlsafe_base64_encode(
                    force_bytes(user.pk)
                )

                token = default_token_generator.make_token(user)

                # Get the frontend URL from environment variable
                # During local development it falls back to localhost.
                frontend_url = os.environ.get(
                    "FRONTEND_URL",
                    "http://localhost:5173"
                ).rstrip("/")

                # Create the password reset link
                reset_link = (
                    f"{frontend_url}/reset-password"
                    f"?uid={uid}&token={token}"
                )

                email_subject = "Reset Your SmartQuiz Password"

                email_body = (
                    f"Hello {user.username},\n\n"
                    f"You requested a password reset for your "
                    f"SmartQuiz student account.\n"
                    f"Please click the exact hyperlink link below "
                    f"to update your login credentials:\n\n"
                    f"{reset_link}\n\n"
                    f"If you did not make this request, please safely "
                    f"ignore this message.\n"
                )

                send_mail(
                    subject=email_subject,
                    message=email_body,
                    from_email='770superuser770@gmail.com',
                    recipient_list=[user.email],
                    fail_silently=False,
                )

            except Exception as e:
                print(
                    "--- SYSTEM CUSTOM MAIL GENERATION FAILURE ---:",
                    str(e)
                )

                return Response(
                    {
                        "error":
                        f"Internal mail delivery issue: {str(e)}"
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        return Response(
            {
                "message":
                "Password reset email sent if account exists."
            },
            status=status.HTTP_200_OK
        )


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

        # Allow only 1 to 30 questions
        limit = max(1, min(limit, 30))

        queryset = Question.objects.filter(
            subject__name__iexact=language_name
        )

        # Filter questions by topic when a topic is provided
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

        send_mail(
            subject=f"SmartQuiz Support Request - {name}",
            message=email_body,
            from_email='770superuser770@gmail.com',
            recipient_list=['770superuser770@gmail.com'],
            fail_silently=False,
        )

        return Response(
            {"message": "Support message sent successfully!"},
            status=status.HTTP_200_OK
        )

    except Exception as e:

        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
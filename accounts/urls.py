from django.urls import path
from . import views
from .views import QuestionListView

urlpatterns = [
    # Core Authentication Routes
    path(
        'signup/',
        views.register,
        name='register'
    ),

    path(
        'login/',
        views.login,
        name='login'
    ),

    # Password Reset Routes
    path(
        'password-reset/',
        views.PasswordResetApiView.as_view(),
        name='password_reset'
    ),

    path(
        'password-reset-confirm/<str:uidb64>/<str:token>/',
        views.PasswordResetConfirmApiView.as_view(),
        name='password_reset_confirm'
    ),

    # Quiz Data Fetching Endpoints
    path(
        'subjects/',
        views.get_subjects,
        name='subjects'
    ),

    path(
        'subjects/<int:subject_id>/questions/',
        views.get_questions_by_subject,
        name='questions'
    ),

    path(
        'scores/save/',
        views.save_quiz_score,
        name='save_score'
    ),

    path(
        'questions/',
        QuestionListView.as_view(),
        name='get_questions'
    ),
]
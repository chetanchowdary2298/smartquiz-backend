from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import QuizScore, Subject, Question

# 1. Define the structural inline view for Quiz Scores tracking
class QuizScoreInline(admin.TabularInline):
    model = QuizScore
    extra = 0  # Prevents Django from displaying empty placeholder rows
    readonly_fields = ('subject', 'score', 'total_questions') # Keeps historical data secure from edits
    can_delete = False # Prevents accidental deletion of student metrics from this panel

# 2. Extend the built-in UserAdmin panel configuration
class UserAdmin(BaseUserAdmin):
    inlines = [QuizScoreInline]

# 3. Securely override the default model registrations layout
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Keep your existing base model registrations active below untouched
@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject', 'text')
    list_filter = ('subject',)

@admin.register(QuizScore)
class QuizScoreAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'subject', 'score', 'total_questions')
    list_filter = ('subject', 'user')
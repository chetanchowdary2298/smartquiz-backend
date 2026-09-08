from django.db import models
from django.contrib.auth.models import User

# 1. Subject Category Table (Python, Java, C++, etc.)
class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

# 2. Questions Table linked directly to a Subject
class Question(models.Model):
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    topic = models.CharField(max_length=100)
    text = models.TextField()
    option_a = models.CharField(max_length=200)
    option_b = models.CharField(max_length=200)
    option_c = models.CharField(max_length=200)
    option_d = models.CharField(max_length=200)
    correct_answer = models.CharField(max_length=1)

    def __str__(self):
        return f"[{self.subject.name} - {self.topic}] {self.text[:50]}"

# 3. Quiz Score Tracking Table for Students
class QuizScore(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    score = models.IntegerField()
    total_questions = models.IntegerField()
    date_taken = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.subject.name}: {self.score}/{self.total_questions}"
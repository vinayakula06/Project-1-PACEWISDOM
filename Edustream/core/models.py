# core/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='student')
    email_otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)
    def __str__(self):
        return self.username
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    class Meta:
        verbose_name_plural = "Categories"
    def __str__(self):
        return self.name
class Course(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses_taught', limit_choices_to={'user_type': 'teacher'})
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='courses')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.title
class CourseContent(models.Model):
    CONTENT_TYPE_CHOICES = (
        ('text', 'Text Lesson'),
        ('video', 'Video Link'),
        ('file', 'Downloadable File'),
        ('quiz', 'Quiz'), 
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='contents')
    title = models.CharField(max_length=200)
    content_type = models.CharField(max_length=10, choices=CONTENT_TYPE_CHOICES)
    text_content = models.TextField(blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    file = models.FileField(upload_to='course_files/', blank=True, null=True) 
    order = models.PositiveIntegerField(default=0) 
    class Meta:
        ordering = ['order']
        verbose_name_plural = "Course Contents"
    def __str__(self):
        return f"{self.course.title} - {self.title}"
class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrolled_courses', limit_choices_to={'user_type': 'student'})
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrollment_date = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    class Meta:
        unique_together = ('student', 'course')
    def __str__(self):
        return f"{self.student.username} enrolled in {self.course.title}"
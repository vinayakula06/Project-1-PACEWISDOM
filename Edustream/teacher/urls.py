# teacher/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('courses/create/', views.course_create, name='course_create'),
    path('courses/<int:pk>/update/', views.course_update, name='course_update'),
    path('courses/<int:pk>/delete/', views.course_delete, name='course_delete'),
    path('courses/<int:course_pk>/content/', views.course_content_manage, name='course_content_manage'),
    path('courses/<int:pk>/students/', views.course_students_view, name='course_students_view'),
]
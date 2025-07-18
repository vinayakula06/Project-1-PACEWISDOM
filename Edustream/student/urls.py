# student/urls.py
from django.urls import path
from . import views
from django.http import HttpResponse 
urlpatterns = [
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('courses/', views.course_list, name='course_list'),
    path('courses/<int:pk>/', views.course_detail, name='course_detail'),
    path('courses/<int:pk>/purchase/', views.course_purchase, name='course_purchase'),
    path('courses/<int:course_pk>/access/', views.course_content_access, name='course_content_access'),
    path('courses/<int:course_pk>/content/<int:content_pk>/', views.view_content_detail, name='view_content_detail'),
    path('paypal/return/', views.paypal_return_view, name='paypal_return'),
    path('paypal/cancel/', views.paypal_cancel_view, name='paypal_cancel'),
    path('paypal/webhook/', views.paypal_webhook_view, name='paypal_webhook'),
]
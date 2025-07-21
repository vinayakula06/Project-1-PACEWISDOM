# student/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.urls import reverse
from django.http import HttpResponse, JsonResponse 
from core.models import Course, Enrollment, CourseContent, Category, User
import requests 
import json 
def is_student(user):
    """Check if the logged-in user is a student."""
    return user.is_authenticated and user.user_type == 'student'
@login_required
@user_passes_test(is_student, login_url='login')
def student_dashboard(request):
    """Displays the student's dashboard with their enrolled courses."""
    enrolled_courses = Enrollment.objects.filter(student=request.user).select_related('course', 'course__teacher').order_by('-enrollment_date')
    return render(request, 'student/dashboard.html', {'enrolled_courses': enrolled_courses})
@login_required
@user_passes_test(is_student, login_url='login')
def course_list(request):
    """Allows students to browse and search for available courses."""
    query = request.GET.get('q')
    category_id = request.GET.get('category')
    
    courses = Course.objects.all().select_related('teacher', 'category')
    if query:
        courses = courses.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(teacher__username__icontains=query) |
            Q(category__name__icontains=query)
        ).distinct()
    if category_id:
        courses = courses.filter(category__id=category_id)
    enrolled_course_ids = Enrollment.objects.filter(student=request.user).values_list('course__id', flat=True)
    available_courses = courses.exclude(id__in=enrolled_course_ids).order_by('title')
    all_categories = Category.objects.all().order_by('name')
    context = {
        'courses': available_courses,
        'query': query,
        'all_categories': all_categories,
        'selected_category': category_id,
    }
    return render(request, 'student/course_list.html', context)

@login_required
@user_passes_test(is_student, login_url='login')
def course_detail(request, pk):
    """Displays details of a specific course."""
    course = get_object_or_404(Course, pk=pk)
    
    print(f"\n--- DEBUG: In course_detail (URL: /student/courses/{pk}/): User {request.user.username} (ID: {request.user.id}), Course ID: {course.title} (ID: {course.id}). Is enrolled: {Enrollment.objects.filter(student=request.user, course=course).exists()} ---")

    is_enrolled = Enrollment.objects.filter(student=request.user, course=course).exists()
    return render(request, 'student/course_detail.html', {'course': course, 'is_enrolled': is_enrolled})

@login_required
@user_passes_test(is_student, login_url='login')
def course_purchase(request, pk):
    """Handles course purchase, differentiating between PayPal and simulated."""
    course = get_object_or_404(Course, pk=pk)
    
    print(f"\n--- DEBUG: Entering course_purchase for user: {request.user.username} (ID: {request.user.id}), Course ID: {pk} ({course.title}) ---")
    print(f"--- DEBUG: request.POST content: {request.POST} ---") # ADDED THIS PRINT

    if Enrollment.objects.filter(student=request.user, course=course).exists():
        messages.info(request, f'You are already enrolled in "{course.title}".')
        print(f"--- DEBUG: User {request.user.username} already enrolled in {course.title}. Redirecting to access page. ---")
        return redirect('course_content_access', course_pk=course.pk)

    if request.method == 'POST':
        try:
            if 'paypal_submit' in request.POST:
                paypal_client_id = settings.PAYPAL_CLIENT_ID
                paypal_secret = settings.PAYPAL_SECRET
                access_token_url = "https://api-m.sandbox.paypal.com/v1/oauth2/token"
                orders_api_url = "https://api-m.sandbox.paypal.com/v2/checkout/orders"
                request.session['course_pk_for_paypal'] = course.pk
                request.session['user_id_for_paypal'] = request.user.id
                # 1. Obtain Access Token
                print("--- DEBUG: Attempting to get PayPal Access Token ---")
                auth_response = requests.post(access_token_url,
                    headers={'Accept': 'application/json', 'Accept-Language': 'en_US'},
                    auth=(paypal_client_id, paypal_secret),
                    data={'grant_type': 'client_credentials'}
                )
                auth_response.raise_for_status()
                access_token = auth_response.json()['access_token']
                print("--- DEBUG: PayPal Access Token obtained. ---")
                # 2. Create Order
                print("--- DEBUG: Attempting to create PayPal Order ---")
                order_data = {
                    "intent": "CAPTURE",
                    "purchase_units": [{
                        "amount": {
                            "currency_code": "USD", # Or your desired currency
                            "value": str(course.price)
                        },
                        "description": f"Course: {course.title}"
                    }],
                    "application_context": {
                        "return_url": request.build_absolute_uri(reverse('paypal_return')),
                        "cancel_url": request.build_absolute_uri(reverse('paypal_cancel'))
                    }
                }
                order_response = requests.post(orders_api_url,
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {access_token}'
                    },
                    data=json.dumps(order_data)
                )
                order_response.raise_for_status()
                order_details = order_response.json()
                print(f"--- DEBUG: PayPal Order created. Order ID: {order_details.get('id')} ---")
                request.session['paypal_order_id'] = order_details['id']
                for link in order_details['links']:
                    if link['rel'] == 'approve':
                        print(f"--- DEBUG: Redirecting to PayPal approval URL: {link['href']} ---")
                        return redirect(link['href'])
                
                messages.error(request, "Could not find PayPal approval URL to redirect.")
                print("--- DEBUG: No PayPal approval URL found. ---")
                return redirect('course_detail', pk=course.pk)
            elif 'simulate_submit' in request.POST:
                print(f"--- DEBUG: SIMULATING ENROLLMENT CREATION (THIS IS ACTIVE NOW) ---")
                enrollment = Enrollment.objects.create(student=request.user, course=course)
                messages.success(request, f'Congratulations! You have successfully purchased "{course.title}".')
                print(f"--- DEBUG: Simulated Enrollment created successfully! ID: {enrollment.id}, Student: {enrollment.student.username}, Course: {enrollment.course.title} ---")
                return redirect('course_content_access', course_pk=course.pk)
            else:
                messages.error(request, "Invalid purchase action. Please select a payment option.")
                print("--- DEBUG: Neither purchase button name found in request. ---")
                return redirect('course_detail', pk=course.pk)

        except requests.exceptions.RequestException as req_e:
            messages.error(request, f"PayPal API communication error: {req_e}. Please try again.")
            print(f"--- DEBUG: PayPal API RequestException: {req_e} ---")
            if req_e.response is not None:
                print(f"--- DEBUG: PayPal API Response Error: {req_e.response.status_code} - {req_e.response.text} ---")
            return redirect('course_detail', pk=course.pk)
        except Exception as e:
            messages.error(request, f'An unexpected error occurred during payment initiation: {e}. Please try again.')
            print(f"--- DEBUG: UNEXPECTED ERROR during purchase initiation: {e} ---")
            return redirect('course_detail', pk=course.pk)
            
    return render(request, 'student/course_purchase_confirm.html', {'course': course})
@login_required
@user_passes_test(is_student, login_url='login')
def paypal_return_view(request):
    """
    Handles PayPal's successful return after payment.
    This is where you'd CAPTURE the payment and create the Enrollment.
    """
    paypal_order_id = request.session.pop('paypal_order_id', None)
    course_pk = request.session.pop('course_pk_for_paypal', None)
    user_id = request.session.pop('user_id_for_paypal', None)

    print(f"\n--- DEBUG: Entering paypal_return_view. Order ID: {paypal_order_id}, Course PK: {course_pk}, User ID: {user_id} ---")

    if not paypal_order_id or not course_pk or not user_id:
        messages.error(request, "Payment session expired or invalid.")
        print("--- DEBUG: Payment session data missing. ---")
        return redirect('student_dashboard')
    
    try:
        course = get_object_or_404(Course, pk=course_pk)
        student = get_object_or_404(User, pk=user_id)
        paypal_client_id = settings.PAYPAL_CLIENT_ID
        paypal_secret = settings.PAYPAL_SECRET

        access_token_url = "https://api-m.sandbox.paypal.com/v1/oauth2/token"
        capture_order_url = f"https://api-m.sandbox.paypal.com/v2/checkout/orders/{paypal_order_id}/capture"

        print("--- DEBUG: Attempting to get Access Token for capture. ---")
        auth_response = requests.post(access_token_url,
            headers={'Accept': 'application/json', 'Accept-Language': 'en_US'},
            auth=(paypal_client_id, paypal_secret),
            data={'grant_type': 'client_credentials'}
        )
        auth_response.raise_for_status()
        access_token = auth_response.json()['access_token']
        print("--- DEBUG: Access Token obtained for capture. ---")

        print("--- DEBUG: Attempting to Capture PayPal Order. ---")
        capture_response = requests.post(capture_order_url,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}'
            }
        )
        capture_response.raise_for_status()
        capture_details = capture_response.json()
        print(f"--- DEBUG: PayPal Capture API response: {capture_details} ---")

        if capture_details.get('status') == 'COMPLETED':
            if not Enrollment.objects.filter(student=student, course=course).exists():
                enrollment = Enrollment.objects.create(student=student, course=course)
                messages.success(request, f"Course '{course.title}' purchased successfully via PayPal!")
                print(f"--- DEBUG: Enrollment for {student.username} in {course.title} created after PayPal capture. Enrollment ID: {enrollment.id} ---")
            else:
                messages.info(request, f"You were already enrolled in '{course.title}'.")
                print(f"--- DEBUG: Enrollment for {student.username} in {course.title} already exists. ---")
            
            return redirect('course_content_access', course_pk=course_pk)
        else:
            messages.error(request, f"PayPal payment not completed. Status: {capture_details.get('status')}. Please try again.")
            print(f"--- DEBUG: PayPal capture status not COMPLETED: {capture_details.get('status')} ---")
            return redirect('course_detail', pk=course_pk)

    except requests.exceptions.RequestException as req_e:
        messages.error(request, f"PayPal API communication error during capture: {req_e}. Please try again.")
        print(f"--- DEBUG: PayPal Capture RequestException: {req_e} ---")
        if req_e.response is not None:
            print(f"--- DEBUG: PayPal Capture Response Error: {req_e.response.status_code} - {req_e.response.text} ---")
        return redirect('course_list')
    except Exception as e:
        messages.error(request, f"An unexpected error occurred during payment verification: {e}. Please try again.")
        print(f"--- DEBUG: UNEXPECTED ERROR in paypal_return_view: {e} ---")
        return redirect('course_list')

@login_required
@user_passes_test(is_student, login_url='login')
def paypal_cancel_view(request):
    """Handles PayPal's cancellation."""
    request.session.pop('paypal_order_id', None)
    request.session.pop('course_pk_for_paypal', None)
    request.session.pop('user_id_for_paypal', None)

    messages.info(request, "PayPal payment was cancelled.")
    print("--- DEBUG: PayPal payment cancelled by user. ---")
    return redirect('course_list')

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def paypal_webhook_view(request):
    """
    Conceptual view for handling PayPal Webhooks (IPN).
    This is critical for reliable payment confirmation.
    """
    if request.method == 'POST':
        print("\n--- DEBUG: Received a PayPal webhook POST request. ---")
        try:
            payload = json.loads(request.body)
            event_type = payload.get('event_type')
            order_id = payload.get('resource', {}).get('id')
            if event_type == 'CHECKOUT.ORDER.COMPLETED':
                print(f"--- DEBUG: Webhook: Order {order_id} completed. ---")
            else:
                print(f"--- DEBUG: Webhook: Unhandled event type: {event_type} ---")
        except Exception as e:
            print(f"--- DEBUG: Error processing webhook: {e} ---")
            return HttpResponse(status=400)

        return HttpResponse(status=200)
    
    print("--- DEBUG: Received non-POST request to PayPal webhook. ---")
    return HttpResponse(status=405)

# --- Course Content Access View ---
@login_required
@user_passes_test(is_student, login_url='login')
def course_content_access(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)
    
    print(f"\n--- DEBUG: Entering course_content_access for user: {request.user.username} (ID: {request.user.id}), Course ID: {course_pk} ({course.title}) ---")
    
    try:
        enrollment = get_object_or_404(Enrollment, student=request.user, course=course)
        print(f"--- DEBUG: Enrollment found successfully for {request.user.username} in {course.title}. Enrollment ID: {enrollment.id} ---")
    except Exception as e:
        print(f"--- DEBUG: ERROR: No Enrollment found for {request.user.username} (ID: {request.user.id}) in {course.title} (ID: {course.id}). Exception: {e} ---")
        messages.error(request, "You are not enrolled in this course or your enrollment could not be verified.")
        return redirect('course_detail', pk=course_pk)

    course_contents = course.contents.all()

    return render(request, 'student/course_content_access.html', {'course': course, 'contents': course_contents})

# --- View Specific Content Detail ---
@login_required
@user_passes_test(is_student, login_url='login')
def view_content_detail(request, course_pk, content_pk):
    course = get_object_or_404(Course, pk=course_pk)
    content = get_object_or_404(CourseContent, pk=content_pk, course=course)

    print(f"\n--- DEBUG: Entering view_content_detail for user: {request.user.username} (ID: {request.user.id}), Course ID: {course_pk}, Content ID: {content_pk} ---")
    
    try:
        get_object_or_404(Enrollment, student=request.user, course=course)
        print(f"--- DEBUG: Enrollment confirmed for {request.user.username} in {course.title} to view content {content.title}. ---")
    except Exception as e:
        print(f"--- DEBUG: ERROR: Enrollment check failed in view_content_detail. Exception: {e} ---")
        messages.error(request, "You do not have access to this course content. Please ensure you are enrolled.")
        return redirect('course_content_access', course_pk=course_pk)

    return render(request, 'student/content_detail.html', {'course': course, 'content': content})

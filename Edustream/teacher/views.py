# teacher/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.forms import inlineformset_factory
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.urls import reverse

from core.models import Course, CourseContent, Enrollment, User
from .forms import CourseForm, CourseContentForm

def is_teacher(user):
    return user.is_authenticated and user.user_type == 'teacher'

@login_required
@user_passes_test(is_teacher, login_url='login')
def teacher_dashboard(request):
    courses = Course.objects.filter(teacher=request.user).order_by('-created_at')
    return render(request, 'teacher/dashboard.html', {'courses': courses})

@login_required
@user_passes_test(is_teacher, login_url='login')
def course_create(request):
    """Handles creation of new courses."""
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.teacher = request.user
            course.save()
            messages.success(request, f'Course "{course.title}" created successfully!')
            students_to_notify = User.objects.filter(
                user_type='student',
                enrolled_courses__course__teacher=request.user
            ).distinct() 
            for student in students_to_notify:
                subject = f'New Course Published by {request.user.get_full_name() or request.user.username}!'
                context = {
                    'student_name': student.username,
                    'author_name': request.user.get_full_name() or request.user.username,
                    'course_title': course.title,
                    'course_description': course.description,
                    'course_pk': course.pk,
                    'protocol': request.scheme,
                    'domain': request.get_host(),
                }
                html_message = render_to_string('emails/new_course_by_author_notification.html', context)
                plain_message = strip_tags(html_message)
                from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@edustream.com')
                try:
                    send_mail(
                        subject,
                        plain_message,
                        from_email,
                        [student.email],
                        html_message=html_message,
                        fail_silently=False,
                    )
                    print(f"Sent new course notification to {student.email} for {course.title}")
                except Exception as e:
                    print(f"Failed to send new course email to {student.email}: {e}")

            return redirect('teacher_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CourseForm()
    return render(request, 'teacher/course_form.html', {'form': form, 'action': 'Create New Course'})

@login_required
@user_passes_test(is_teacher, login_url='login')
def course_update(request, pk):
    """Handles updating an existing course."""
    course = get_object_or_404(Course, pk=pk, teacher=request.user)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, f'Course "{course.title}" updated successfully!')
            return redirect('teacher_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CourseForm(instance=course)
    return render(request, 'teacher/course_form.html', {'form': form, 'action': 'Update Course'})

@login_required
@user_passes_test(is_teacher, login_url='login')
def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk, teacher=request.user)
    if request.method == 'POST':
        course.delete()
        messages.success(request, f'Course "{course.title}" deleted successfully!')
        return redirect('teacher_dashboard')
    return render(request, 'teacher/course_confirm_delete.html', {'course': course})
@login_required
@user_passes_test(is_teacher, login_url='login')
def course_content_manage(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk, teacher=request.user)
    CourseContentFormSet = inlineformset_factory(
        Course,
        CourseContent,
        form=CourseContentForm,
        extra=1,
        can_delete=True,
        fields=('title', 'content_type', 'text_content', 'video_url', 'file', 'order')
    )
    if request.method == 'POST':
        formset = CourseContentFormSet(request.POST, request.FILES, instance=course)
        if formset.is_valid():
            new_content_added_flag = False
            for form in formset.forms:
                if form.has_changed() and not form.instance.pk and not form.cleaned_data.get('DELETE'):
                    new_content_added_flag = True
                    break
            formset.save()
            messages.success(request, 'Course content updated successfully!')
            if new_content_added_flag:
                enrolled_students = Enrollment.objects.filter(course=course).select_related('student')
                for enrollment in enrolled_students:
                    student_email = enrollment.student.email
                    context = {
                        'student_name': enrollment.student.username,
                        'course_title': course.title,
                        'teacher_name': course.teacher.get_full_name() or course.teacher.username,
                        'course_pk': course.pk,
                        'protocol': request.scheme,
                        'domain': request.get_host(),
                    }
                    html_message = render_to_string('emails/new_topic_notification.html', context)
                    plain_message = strip_tags(html_message)
                    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@edustream.com')
                    try:
                        send_mail(
                            f'New Content Added to Your Course: {course.title}',
                            plain_message,
                            from_email,
                            [student_email],
                            html_message=html_message,
                            fail_silently=False,
                        )
                        print(f"Sent new topic email to {student_email} for course {course.title}")
                    except Exception as e:
                        print(f"Failed to send new topic email to {student_email}: {e}")

            return redirect('course_content_manage', course_pk=course.pk)
        else:
            messages.error(request, 'Please correct the errors in the content forms.')
    else:
        formset = CourseContentFormSet(instance=course)

    return render(request, 'teacher/course_content_manage.html', {'course': course, 'formset': formset})

@login_required
@user_passes_test(is_teacher, login_url='login')
def course_students_view(request, pk):
    """Displays a list of students who have purchased a specific course."""
    course = get_object_or_404(Course, pk=pk, teacher=request.user)
    enrolled_students = Enrollment.objects.filter(course=course).select_related('student').order_by('student__username')
    return render(request, 'teacher/course_students_view.html', {'course': course, 'enrolled_students': enrolled_students})
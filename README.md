# EduStream: An Online Learning Platform

EduStream is a dynamic online learning platform designed to connect passionate teachers with eager students. It enables instructors to create and manage their courses, set prices, and deliver diverse content, while providing students with a seamless experience to explore, purchase, and access educational materials.

## Project Purpose

The primary goal of this project is to build a comprehensive online learning ecosystem. It allows teachers to monetize their expertise by offering courses and facilitates students' learning journeys through a user-friendly interface for course discovery, secure enrollment, and content consumption. The platform incorporates essential features like two-factor authentication, robust course management, and integrated payment processing.

## Features

EduStream offers a rich set of functionalities tailored for both teachers and students:

### Student Features

1.  **Secure Authentication:** Students can easily sign up and log in to the platform, with an added layer of security provided by **2-Factor Authentication (2FA)** using email-based One-Time Passwords (OTPs).
2.  **Course Exploration:** Browse and discover a wide variety of courses available on the platform.
3.  **Advanced Search:** Efficiently search for specific courses using criteria such as title, instructor, category, or keywords.
4.  **Course Enrollment/Purchase:** Students can subscribe to or purchase courses, gaining full access to their content.
5.  **Content Access:** View and read course materials to which they have subscribed.
6.  **Dashboard:** A personalized student dashboard displaying all enrolled courses.

### Teacher Features

1.  **Secure Authentication:** Teachers also benefit from **2-Factor Authentication (2FA)** via email OTP for secure login.
2.  **Course Lifecycle Management:**
      * **Create Courses:** Easily create new courses, defining their title, description, price, and category.
      * **Update Courses:** Modify existing course details as needed.
      * **Delete Courses:** Permanently remove courses from the platform.
3.  **Course Content Management:** Add, edit, and delete various types of course content, including:
      * Text lessons
      * Video links (e.g., YouTube embeds)
      * Downloadable files
      * Quiz placeholders (for future expansion)
4.  **Student Enrollment Tracking:** View a comprehensive list of students who have purchased or enrolled in their courses.

### Additional Features

  * **PayPal Payment Gateway Integration:** The platform integrates with PayPal (sandbox mode for demonstration) for secure course purchases, allowing real-world transaction flows.
  * **Email Notifications:**
      * Students receive an email notification when **new content (topic)** is added to a course they have already purchased.
      * Students receive an email notification when a **new course is designed by an author** whose other courses they have previously purchased.

-----

### Project 1: API Usage and Functionality

This project, "EduStream," serves as **Project 1** and provides a comprehensive set of APIs to power the online learning platform. Below are the key API endpoints (URLs) built to support all student and teacher operations described in the features above. These APIs handle all the core functionalities, from user authentication and course management to content access and payment processing.

## API Endpoints (URLs)

Here's a breakdown of the key API endpoints (URLs) and their purposes within the EduStream platform:

### Core (Authentication & General)

  * **Homepage:**
      * **URL:** `/`
      * **Purpose:** Serves as the landing page for the application.
      * **Handled by:** `EduStream/urls.py` via `TemplateView`
      * **Template:** `templates/home.html`
  * **User Sign Up:**
      * **URL:** `/accounts/signup/`
      * **Purpose:** Allows new users (students or teachers) to create an account.
      * **Handled by:** `core.views.signup_view`
      * **Template:** `templates/registration/signup.html`
  * **User Login:**
      * **URL:** `/accounts/login/`
      * **Purpose:** Authenticates users and initiates the 2FA OTP process.
      * **Handled by:** `core.views.login_view`
      * **Template:** `templates/registration/login.html`
  * **Verify OTP:**
      * **URL:** `/accounts/verify-otp/`
      * **Purpose:** Verifies the One-Time Password sent to the user's email for 2FA.
      * **Handled by:** `core.views.verify_otp_view`
      * **Template:** `templates/registration/verify_otp.html`
  * **User Logout:**
      * **URL:** `/accounts/logout/`
      * **Purpose:** Logs out the currently authenticated user.
      * **Handled by:** `core.views.logout_view`

### Student-Specific

  * **Student Dashboard:**
      * **URL:** `/student/dashboard/`
      * **Purpose:** Displays the enrolled courses for a logged-in student.
      * **Handled by:** `student.views.student_dashboard`
      * **Template:** `templates/student/dashboard.html`
  * **Browse Courses:**
      * **URL:** `/student/courses/`
      * **Purpose:** Allows students to view all available courses and search/filter them.
      * **Handled by:** `student.views.course_list`
      * **Template:** `templates/student/course_list.html`
  * **Course Detail:**
      * **URL:** `/student/courses/<int:pk>/`
      * **Purpose:** Shows detailed information about a specific course.
      * **Handled by:** `student.views.course_detail`
      * **Template:** `templates/student/course_detail.html`
  * **Course Purchase:**
      * **URL:** `/student/courses/<int:pk>/purchase/`
      * **Purpose:** Initiates the course purchase process (simulated or via PayPal).
      * **Handled by:** `student.views.course_purchase`
      * **Template:** `templates/student/course_purchase_confirm.html`
  * **Access Course Content:**
      * **URL:** `/student/courses/<int:course_pk>/access/`
      * **Purpose:** Displays all content modules for a purchased course.
      * **Handled by:** `student.views.course_content_access`
      * **Template:** `templates/student/course_content_access.html`
  * **View Specific Content:**
      * **URL:** `/student/courses/<int:course_pk>/content/<int:content_pk>/`
      * **Purpose:** Displays the details of a specific course content item (text, video, file, or quiz).
      * **Handled by:** `student.views.view_content_detail`
      * **Template:** `templates/student/content_detail.html`
  * **PayPal Return URL:**
      * **URL:** `/student/paypal/return/`
      * **Purpose:** Callback URL for successful PayPal payments to finalize enrollment.
      * **Handled by:** `student.views.paypal_return_view`
  * **PayPal Cancel URL:**
      * **URL:** `/student/paypal/cancel/`
      * **Purpose:** Callback URL for cancelled PayPal payments.
      * **Handled by:** `student.views.paypal_cancel_view`
  * **PayPal Webhook (IPN):**
      * **URL:** `/student/paypal/webhook/`
      * **Purpose:** Designed to receive asynchronous payment notifications from PayPal (critical for reliable payment confirmation in a production environment).
      * **Handled by:** `student.views.paypal_webhook_view`

### Teacher-Specific

  * **Teacher Dashboard:**
      * **URL:** `/teacher/dashboard/`
      * **Purpose:** Displays all courses created by the logged-in teacher, with options to manage them.
      * **Handled by:** `teacher.views.teacher_dashboard`
      * **Template:** `templates/teacher/dashboard.html`
  * **Create Course:**
      * **URL:** `/teacher/courses/create/`
      * **Purpose:** Allows a teacher to create a new course.
      * **Handled by:** `teacher.views.course_create`
      * **Template:** `templates/teacher/course_form.html`
  * **Update Course:**
      * **URL:** `/teacher/courses/<int:pk>/update/`
      * **Purpose:** Allows a teacher to modify details of an existing course.
      * **Handled by:** `teacher.views.course_update`
      * **Template:** `templates/teacher/course_form.html`
  * **Delete Course:**
      * **URL:** `/teacher/courses/<int:pk>/delete/`
      * **Purpose:** Confirms and deletes a specific course.
      * **Handled by:** `teacher.views.course_delete`
      * **Template:** `templates/teacher/course_confirm_delete.html`
  * **Manage Course Content:**
      * **URL:** `/teacher/courses/<int:course_pk>/content/`
      * **Purpose:** Allows a teacher to add, edit, and delete content modules within a course using an inline formset.
      * **Handled by:** `teacher.views.course_content_manage`
      * **Template:** `templates/teacher/course_content_manage.html`
  * **View Enrolled Students:**
      * **URL:** `/teacher/courses/<int:pk>/students/`
      * **Purpose:** Displays a list of students enrolled in a specific course.
      * **Handled by:** `teacher.views.course_students_view`
      * **Template:** `templates/teacher/course_students_view.html`

-----

## Tech Stack

The EduStream platform is built using the following technologies:

  * **Backend Framework:** Python (Django)
  * **Frontend:** HTML, CSS (Bootstrap 5.3), JavaScript (jQuery)
  * **Database:** SQLite3 (default for local development)
  * **Payment Gateway:** PayPal (Sandbox API)
  * **Email Service:** SMTP for sending email notifications (configured with Gmail in `settings.py`)

## File Structure

The project follows a standard Django project structure, organized into a main project directory (`EduStream`) and several Django applications (`core`, `teacher`, `student`, `static`, `templates`, `media`):

```
EduStream/
├── EduStream/                  # Main Django project settings
│   ├── __init__.py
│   ├── settings.py             # Project configurations (database, static, media, PayPal, email)
│   ├── urls.py                 # Main URL dispatcher
│   └── wsgi.py
├── core/                       # Core application for common functionalities (users, categories, courses, enrollments)
│   ├── migrations/
│   │   └── 0001_initial.py     # Database schema migrations
│   ├── templatetags/
│   │   ├── __init__.py
│   │   └── custom_filters.py   # Custom Django template filters
│   ├── __init__.py
│   ├── admin.py                # Django Admin configurations for core models
│   ├── app.py                  # App configuration
│   ├── forms.py                # Forms for user signup and OTP verification
│   ├── models.py               # Database models (User, Category, Course, CourseContent, Enrollment)
│   ├── tests.py
│   └── urls.py                 # URLs for authentication (signup, login, OTP, logout)
│   └── views.py                # Views for authentication and core functionalities
├── manage.py                   # Django's command-line utility
├── media/                      # Directory for user-uploaded files (e.g., course files)
├── static/                     # Static assets (CSS, JS, images)
│   └── css/
│       └── style.css           # Custom CSS styles
├── student/                    # Student-specific application
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py                 # URLs for student dashboard, course Browse, purchase, content access
│   └── views.py                # Views handling student functionalities
├── teacher/                    # Teacher-specific application
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py                # Forms for course and course content management
│   ├── models.py
│   ├── tests.py
│   ├── urls.py                 # URLs for teacher dashboard, course CRUD, content management, student views
│   └── views.py                # Views handling teacher functionalities
└── templates/                  # Base directory for all HTML templates
    ├── emails/                 # Email template
    │   ├── new_course_by_author_notification.html
    │   └── new_topic_notification.html
    ├── registration/           # Authentication related templates
    │   ├── login.html
    │   ├── signup.html
    │   └── verify_otp.html
    ├── student/                # Student-specific templates
    │   ├── content_detail.html
    │   ├── course_content_access.html
    │   ├── course_detail.html
    │   ├── course_list.html
    │   ├── course_purchase_confirm.html
    │   └── dashboard.html
    ├── teacher/                # Teacher-specific templates
    │   ├── course_confirm_delete.html
    │   ├── course_content_manage.html
    │   ├── course_form.html
    │   ├── course_students_view.html
    │   └── dashboard.html
    └── base.html               # Base template for consistent layout
    └── home.html               # Homepage template
```

## How to Run Locally

Follow these steps to set up and run the EduStream project on your local machine:

### Prerequisites

  * Python 3.8+
  * pip (Python package installer)

### Setup Instructions

1.  **Clone the Repository:**
    (Assuming you have the project files, if not, this would be the step to get them)

    ```bash
    git clone <repository_url>
    cd EduStream
    ```

    *(Note: Replace `<repository_url>` with the actual URL if this were a Git repository.)*

2.  **Create a Virtual Environment:**
    It's good practice to use a virtual environment to manage project dependencies.

    ```bash
    python -m venv venv
    ```

3.  **Activate the Virtual Environment:**

      * **On macOS/Linux:**
        ```bash
        source venv/bin/activate
        ```
      * **On Windows:**
        ```bash
        venv\Scripts\activate
        ```

4.  **Install Dependencies:**
    Install the required Python packages (Django, Requests for PayPal API).

    ```bash
    pip install Django requests
    ```

    *(If you had a `requirements.txt` file, you would run `pip install -r requirements.txt`)*

5.  **Database Migrations:**
    Apply the initial database migrations to create the necessary tables.

    ```bash
    python manage.py makemigrations core
    python manage.py migrate
    ```

6.  **Create a Superuser (Admin Account):**
    This allows you to access the Django admin panel and create initial data like categories, teachers, and courses.

    ```bash
    python manage.py createsuperuser
    ```

    Follow the prompts to set a username, email, and password.

7.  **Configure Environment Variables (Important\!)**
    The project requires configuration for PayPal API credentials and email settings, which are used for payments and notifications. For security, these should be stored as environment variables rather than hardcoded in `settings.py`.

      * **PayPal API Credentials:**
        You will need your `PAYPAL_CLIENT_ID` and `PAYPAL_SECRET` from your PayPal Developer Dashboard (use sandbox credentials for testing).
      * **Email Settings:**
        Configure `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, and `DEFAULT_FROM_EMAIL` for sending OTPs and notifications. If you are using Gmail, you will typically need to generate an "App Password" to allow applications to send emails, as direct password login for third-party apps is often blocked. Refer to Google's official documentation on App Passwords for instructions.

    **Example of how you might set these variables (e.g., in your shell or a `.env` file):**

    ```bash
    export PAYPAL_CLIENT_ID='your_paypal_client_id'
    export PAYPAL_SECRET='your_paypal_secret'
    export EMAIL_HOST_USER='your_email@example.com'
    export EMAIL_HOST_PASSWORD='your_email_app_password' # For Gmail, use an App Password
    export DEFAULT_FROM_EMAIL='your_email@example.com'
    ```

    You would then update your `settings.py` to read these values from environment variables (e.g., using `os.environ.get()` or a library like `python-dotenv`).

8.  **Run the Development Server:**
    Start the Django development server.

    ```bash
    python manage.py runserver
    ```

9.  **Access the Application:**
    Open your web browser and navigate to:
    `http://127.0.0.1:8000/`

    You can also access the Django admin panel at:
    `http://127.0.0.1:8000/admin/` (use the superuser credentials created earlier)

Enjoy exploring EduStream\!

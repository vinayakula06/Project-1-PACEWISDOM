# core/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User
class UserSignUpForm(UserCreationForm):
    user_type = forms.ChoiceField(
        choices=User.USER_TYPE_CHOICES,
        initial='student',
        widget=forms.RadioSelect,
        help_text="Select whether you are a student or a teacher."
    )
    email = forms.EmailField(
        required=True,
        help_text="Required. Valid email address."
    )
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('user_type', 'email',)
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered. Please use a different one or log in.")
        return email
class EmailOTPForm(forms.Form):
    otp = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={'placeholder': 'Enter 6-digit OTP', 'class': 'form-control'}),
        help_text="Check your email for the One-Time Password."
    )
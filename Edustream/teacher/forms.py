# teacher/forms.py
from django import forms
from core.models import Course, CourseContent, Category
class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'price', 'category']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'Enter course description'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Course Title'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'title': 'Course Title',
            'description': 'Course Description',
            'price': 'Course Price ($)',
            'category': 'Course Category',
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate categories dynamically
        self.fields['category'].queryset = Category.objects.all().order_by('name')
        # Add a default empty option for category
        self.fields['category'].empty_label = "Select a Category"


class CourseContentForm(forms.ModelForm):
    class Meta:
        model = CourseContent
        fields = ['title', 'content_type', 'text_content', 'video_url', 'file', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Content Title'}),
            'content_type': forms.Select(attrs={'class': 'form-control'}),
            'text_content': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Enter text content here...'}),
            'video_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'e.g., https://www.youtube.com/watch?v=dQw4w9WgXcQ'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Order'}),
        }
        labels = {
            'title': 'Content Title',
            'content_type': 'Type',
            'text_content': 'Text Content',
            'video_url': 'Video URL',
            'file': 'Downloadable File',
            'order': 'Display Order',
        }
    def clean(self):
        cleaned_data = super().clean()
        content_type = cleaned_data.get('content_type')
        text_content = cleaned_data.get('text_content')
        video_url = cleaned_data.get('video_url')
        file = cleaned_data.get('file')

        if content_type == 'text' and not text_content:
            self.add_error('text_content', 'Text content is required for text lessons.')
        if content_type == 'video' and not video_url:
            self.add_error('video_url', 'Video URL is required for video lessons.')
        if content_type == 'file' and not file:
            self.add_error('file', 'A file is required for downloadable content.')
        
        return cleaned_data
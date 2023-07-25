from django import forms
from blog.models import Comment
class CommentForm(forms.ModelForm):
    content = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'md-textarea form-control',
        'placeholder': 'Your thoughts matters, comment here ...',
        'rows': '1',
    }))
    class Meta:
        model = Comment
        fields = ('content', )
from django.contrib.auth import get_user_model
from django.forms import ModelForm

from .models import Post

User = get_user_model()


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group',)
        help_texts = {'text': 'Текст публикации', 'group': 'Пожалуйста, '
                      'выберете наиболее подходящую группу из списка или '
                      'оставьте без группы'}

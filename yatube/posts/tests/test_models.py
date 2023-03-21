from django.test import TestCase

from ..models import Group, Post, User

AUTHOR_USERNAME = 'HasNoName'
USER_USERNAME = 'TestUser'
GROUP_TITLE = 'Тестовая группа'
GROUP_SLUG = 'test-slug'
GROUP_DESCRIPTION = 'Тестовое описание'
POST_TEXT = 'Тестовый пост'


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=AUTHOR_USERNAME)
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=POST_TEXT,
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = PostModelTest.post  # Обратите внимание на синтаксис
        group = PostModelTest.group
        expected_object_str_post = post.text[:15]
        expected_object_str_group = group.title

        field_model = {
            'post': post,
            'group': group,
        }

        field_str = {
            'post': expected_object_str_post,
            'group': expected_object_str_group,
        }
        for model, expected_value in field_str.items():
            with self.subTest(model=model):
                self.assertEqual(expected_value, str(field_model[model]))

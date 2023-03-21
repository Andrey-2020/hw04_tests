from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post, User

AUTHOR_USERNAME = 'HasNoName'
USER_USERNAME = 'TestUser'
GROUP_TITLE = 'Тестовая группа'
GROUP_SLUG = 'test-slug'
GROUP_DESCRIPTION = 'Тестовое описание'
POST_TEXT = 'Тестовый пост'

INDEX_URL = reverse('posts:index')
GROUP_LIST_URL = reverse('posts:group_list', args=[GROUP_SLUG])
PROFILE_URL = reverse('posts:profile', args=[AUTHOR_USERNAME])
POST_CREATE_URL = reverse('posts:post_create')
FORM_FIELD_TEXT_HELP_TEXT = 'Текст публикации'
FORM_FIELD_GROUP_HELP_TEXT = ('Пожалуйста, '
                              'выберете наиболее подходящую группу из списка '
                              'или оставьте без группы')


class TaskCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=AUTHOR_USERNAME)
        cls.form = PostForm()
        cls.post = Post.objects.create(
            author=cls.user,
            text=POST_TEXT,
        )
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
        cls.POST_DETAIL_URL = reverse('posts:post_detail', kwargs={
            'post_id': cls.post.pk})
        cls.POST_EDIT_URL = reverse('posts:post_edit', kwargs={
            'post_id': cls.post.pk})

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(TaskCreateFormTests.user)

    def test_form_help_text(self):
        """Проверка поля help_text"""
        text_help_text = TaskCreateFormTests.form.fields['text'].help_text
        group_help_text = TaskCreateFormTests.form.fields['group'].help_text
        self.assertEquals(text_help_text, FORM_FIELD_TEXT_HELP_TEXT)
        self.assertEquals(group_help_text, FORM_FIELD_GROUP_HELP_TEXT)

    def test_create_task(self):
        """Валидная форма создает запись в Post."""
        tasks_count = Post.objects.count()

        form_data = {
            'text': 'Тестовый текст',
            'author': TaskCreateFormTests.user,
        }

        response = self.authorized_client.post(
            POST_CREATE_URL,
            data=form_data
        )
        self.assertRedirects(response, PROFILE_URL)

        self.assertEqual(Post.objects.count(), tasks_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                author=TaskCreateFormTests.user,
            ).exists()
        )

    def test_post_edit(self):
        """Валидная форма изменяет запись в Post."""
        tasks_count = Post.objects.count()
        form_data = {
            'text': 'Измененный текст',
            'group': TaskCreateFormTests.group.id,
        }
        response = self.authorized_client.post(
            TaskCreateFormTests.POST_EDIT_URL,
            follow=True,
            data=form_data
        )
        self.assertEqual(Post.objects.count(), tasks_count)

        self.assertRedirects(response, TaskCreateFormTests.POST_DETAIL_URL)

        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                author=TaskCreateFormTests.user,
                group=TaskCreateFormTests.group.id,
            ).exists()
        )

    def test_redirect(self):
        """Проверяем, что корректно работает автоматическое перенаправление."""
        response = self.guest_client.get(
            TaskCreateFormTests.POST_EDIT_URL,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        redirect_url = (
            reverse('users:login') + '?next='
            + TaskCreateFormTests.POST_EDIT_URL
        )
        self.assertRedirects(response, redirect_url)

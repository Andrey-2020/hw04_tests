from django import forms
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User

POSTS_PER_PAGE = 10


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


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username=AUTHOR_USERNAME)

        cls.COUNT_OF_POSTS = 13
        cls.COUNT_ON_PAGE = 10
        cls.OTHERS_OF_POSTS = 3
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
        Post.objects.bulk_create([
            Post(
                text=f'{POST_TEXT} {i}', author=cls.author, group=cls.group
            ) for i in range(cls.COUNT_OF_POSTS)
        ])

        cls.templates_pages_names = {
            INDEX_URL: 'posts/index.html',
            GROUP_LIST_URL: 'posts/group_list.html',
            PROFILE_URL: 'posts/profile.html',
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PaginatorViewsTest.author)

    def test_first_page_contains_ten_records(self):
        for reverse_name in (PaginatorViewsTest.
                             templates_pages_names.keys()):
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertEqual(
                    len(response.context['page_obj']),
                    POSTS_PER_PAGE)

    def test_second_page_contains_three_records(self):
        for reverse_name in (PaginatorViewsTest.
                             templates_pages_names.keys()):
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name + '?page=2')
                self.assertEqual(len(response.context['page_obj']),
                                 PaginatorViewsTest.OTHERS_OF_POSTS)


class TaskPagesTests(TestCase):
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
            group=cls.group,
        )

        cls.POST_DETAIL_URL = reverse('posts:post_detail', kwargs={
            'post_id': TaskPagesTests.post.pk})
        cls.POST_EDIT_URL = reverse('posts:post_edit', kwargs={
            'post_id': TaskPagesTests.post.pk})

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(TaskPagesTests.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            INDEX_URL: 'posts/index.html',
            GROUP_LIST_URL: 'posts/group_list.html',
            PROFILE_URL: 'posts/profile.html',
            TaskPagesTests.POST_DETAIL_URL: 'posts/post_detail.html',
            POST_CREATE_URL: 'posts/create_post.html',
            TaskPagesTests.POST_EDIT_URL: 'posts/create_post.html'
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(INDEX_URL)
        first_object = response.context['page_obj'][0]
        task_title_0 = first_object.author
        task_text_0 = first_object.text
        self.assertEqual(task_title_0, TaskPagesTests.user)
        self.assertEqual(task_text_0, POST_TEXT)

    def test_group_posts_pages_show_correct_context(self):
        """Шаблон group_posts сформирован с правильным контекстом."""
        response = (self.authorized_client.
                    get(GROUP_LIST_URL))
        first_object = response.context['page_obj'][0]
        task_title_0 = first_object.author
        task_text_0 = first_object.text
        task_group_0 = first_object.group
        self.assertEqual(task_title_0, TaskPagesTests.user)
        self.assertEqual(task_text_0, POST_TEXT)
        self.assertEqual(task_group_0.slug, GROUP_SLUG)

    def test_profile_pages_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = (self.authorized_client.
                    get(PROFILE_URL))
        first_object = response.context['page_obj'][0]
        task_title_0 = first_object.author
        task_text_0 = first_object.text
        task_group_0 = first_object.group
        author = response.context['author']
        self.assertEqual(task_title_0, TaskPagesTests.user)
        self.assertEqual(task_text_0, POST_TEXT)
        self.assertEqual(task_group_0.slug, GROUP_SLUG)
        self.assertEqual(author, TaskPagesTests.user)

    def test_post_detail_pages_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = (self.authorized_client.
                    get(TaskPagesTests.POST_DETAIL_URL))
        self.assertEqual(response.context['post'].author, TaskPagesTests.user)
        self.assertEqual(response.context['post'].text, POST_TEXT)

    def test_post_create_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(POST_CREATE_URL)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(TaskPagesTests.POST_EDIT_URL)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        is_edit = response.context.get('is_edit')
        self.assertTrue(is_edit)
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

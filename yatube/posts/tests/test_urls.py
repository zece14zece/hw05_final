from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
    def test_homepage(self):
        # Делаем запрос к главной странице и проверяем статусA
        response = self.client.get("/")
        # Утверждаем, что для прохождения теста код должен быть равен 200
        self.assertEqual(response.status_code, 200)


class TaskURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(
            username="test_name",
        )

        cls.group = Group.objects.create(
            title="Заголовок",
            slug="test_slug",
        )

        cls.post = Post.objects.create(
            author=cls.author,
            text="Текст, написанный для проверки",
            group=cls.group,
        )
        cls.guest_client = Client()
        # Создаем пользователя
        cls.user = User.objects.create_user(username="HasNoName")
        # Создаем второй клиент
        cls.authorized_client = Client()
        # Авторизуем пользователя
        cls.authorized_client.force_login(cls.user)
        cls.authorized_client_author = Client()
        cls.authorized_client_author.force_login(cls.author)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Шаблоны по адресам
        templates_url_names = {
            "posts/index.html": reverse("posts:index"),
            "posts/group_list.html": reverse(
                "posts:group_posts", kwargs={"slug": self.group.slug}
            ),
            "posts/profile.html": reverse(
                "posts:profile", kwargs={"username": self.author.username}
            ),
            "posts/post_detail.html": reverse(
                "posts:post_detail", kwargs={"post_id": self.post.id}
            ),
            "posts/create_post.html": reverse(
                "posts:post_edit", kwargs={"post_id": self.post.id}
            ),
        }

        for template, adress in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client_author.get(adress)
                self.assertTemplateUsed(response, template)

    def test_urls_for_all_users(self):
        urls_and_response_statuses = {
            reverse("posts:index"): 200,
            reverse("posts:profile",
                    kwargs={"username": self.user.username}): 200,
            reverse("posts:group_posts",
                    kwargs={"slug": self.group.slug}): 200,
            reverse("posts:post_detail",
                    kwargs={"post_id": self.post.id}): 200,
            "/unexisting_page/": 404,
        }

        for urls, statuses in urls_and_response_statuses.items():
            with self.subTest(urls=urls):
                response = self.client.get(urls)
                self.assertEqual(response.status_code, statuses)

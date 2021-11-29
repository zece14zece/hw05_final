import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Follow, Group, Post
from .fixtures import ObjectsCreate, UsersCreate

User = get_user_model()

User = get_user_model()
SLUG_1 = "1"
SLUG_2 = "2"
GROUP_1 = reverse("posts:group_posts", kwargs={"slug": SLUG_1})
GROUP_2 = reverse("posts:group_posts", kwargs={"slug": SLUG_2})


class TaskViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_a = User.objects.create_user(username="user_a")
        cls.author_p = User.objects.create_user(username="author_p")
        cls.group = Group.objects.create(
            slug=SLUG_1,
            title="test-title",
            description="test-desc",
        )

    def setUp(self):
        self.author = User.objects.create(
            username="test_name",
        )
        self.post = Post.objects.create(
            author=self.author,
            text="Текст, написанный для проверки",
            group=self.group,
        )
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_pages_uses_correct_template(self):
        templates_pages_names = {
            reverse("posts:index"): "posts/index.html",
            reverse(
                "posts:group_posts", kwargs={"slug": self.group.slug}
            ): "posts/group_list.html",
            reverse(
                "posts:profile", kwargs={"username": self.author.username}
            ): "posts/profile.html",
            reverse(
                "posts:post_detail", kwargs={"post_id": self.post.id}
            ): "posts/post_detail.html",
            reverse("posts:post_create"): "posts/create_post.html",
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)


class TaskPaginatorsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_a = User.objects.create_user(username="user_a")
        cls.author_p = User.objects.create_user(username="author_p")
        cls.group = Group.objects.create(
            slug=SLUG_1,
            title="test-title",
            description="test-desc",
        )
        cls.posts = (
            Post(text=f"text{i}", author=cls.user_a,
                 group=cls.group) for i in range(13)
        )
        Post.objects.bulk_create(cls.posts, 13)
        cls.TEMP = (
            reverse("posts:index"),
            reverse("posts:group_posts", kwargs={"slug": cls.group.slug}),
            reverse("posts:profile", kwargs={"username": cls.user_a.username}),
        )

    def setUp(self):
        self.guest_client = Client()

    def test_item_posts_per_page(self):
        for page_name in self.TEMP:
            with self.subTest(page_name=page_name):
                response = self.guest_client.get(page_name)
                self.assertEqual(len(response.context["page_obj"]), 10)
                response = self.guest_client.get(page_name + "?page=2")
                self.assertEqual(len(response.context["page_obj"]), 3)


class AnotherGroupTests(TestCase):
    def setUp(self):
        self.author_p = User.objects.create_user(username="author_p")
        self.group_1 = Group.objects.create(
            slug="1", title="testtitle", description="testdesc"
        )
        self.group_2 = Group.objects.create(
            slug="2", title="testtitle2", description="testdesc2"
        )
        Post.objects.create(author=self.author_p,
                            text="text_2", group=self.group_2)
        Post.objects.create(author=self.author_p,
                            text="text_1", group=self.group_1)
        self.guest_client = Client()
        self.a_c_author = Client()
        self.a_c_author.force_login(self.author_p)

    def test_post_in_2_group_2(self):
        response = self.a_c_author.get(GROUP_1)
        self.assertEqual(response.context["page_obj"][0].group.id, 1)
        response = self.a_c_author.get(GROUP_2)
        self.assertEqual(response.context["page_obj"][0].group.id, 2)

    def test_index_correct_context(self):
        response = self.guest_client.get(reverse("posts:index"))
        self.assertEqual(len(response.context["page_obj"]), 2)
        self.assertEqual(response.context["posts"].count(), 2)

    def test_group_list_correct_context(self):
        response = self.guest_client.get(
            reverse("posts:group_posts", kwargs={"slug": self.group_1.slug})
        )
        first_object = response.context["page_obj"][0]
        self.assertEqual(first_object.group, self.group_1)

    def test_profile_correct_context(self):
        response = self.guest_client.get(
            reverse("posts:profile",
                    kwargs={"username": self.author_p.username})
        )
        self.assertEqual(response.context["page_obj"][0].author, self.author_p)


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PictureTest(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.author = User.objects.create(username="test_name")

        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.author)

        self.group = Group.objects.create(
            title="Заголовок",
            slug="test_slug",
        )

        self.small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )

        self.uploaded = SimpleUploadedFile(
            name="small.gif",
            content=self.small_gif,
            content_type="image/gif",
        )
        self.post = Post.objects.create(
            author=self.author,
            text="Текст, написанный для проверки",
            group=self.group,
            image=self.uploaded,
        )

    def test_index_image(self):
        response = self.authorized_client_author.get(reverse("posts:index"))
        obj = response.context["page_obj"][0]
        self.assertTrue(obj.image)

    def test_profile_image(self):
        response = self.authorized_client_author.get(
            reverse("posts:profile", kwargs={"username": self.author.username})
        )
        user = User.objects.get(username="test_name")
        obj = response.context["page_obj"][0]
        self.assertEqual(obj.text, "Текст, написанный для проверки")
        self.assertEqual(obj.author, user)
        self.assertTrue(obj.image)

    def test_group_image(self):
        response = self.authorized_client_author.get(
            reverse("posts:group_posts", kwargs={"slug": self.group.slug})
        )
        obj = response.context["page_obj"][0]
        self.assertEqual(obj.text, "Текст, написанный для проверки")
        self.assertEqual(obj.author, self.author)
        self.assertEqual(obj.group, self.group)
        self.assertTrue(obj.image)

    def test_post_detail_image(self):
        response = self.authorized_client_author.get(
            reverse("posts:post_detail", kwargs={"post_id": self.post.id})
        )
        obj = response.context.get("post")
        self.assertEqual(obj.text, "Текст, написанный для проверки")
        self.assertEqual(obj.author, self.author)
        self.assertEqual(obj.group, self.group)
        self.assertTrue(obj.image)


class TestCache(TestCase):
    def setUp(self):
        self.post_author = UsersCreate.author_create()
        self.AUTHOR = UsersCreate.authorized_author_client_create()
        self.GROUP = ObjectsCreate.group_create()
        self.POST = ObjectsCreate.post_create(
            self.GROUP, self.post_author, "текст поста"
        )

    def test_cache(self):
        response = self.AUTHOR.get(reverse("posts:index"))
        not_deleted = response.content
        post_to_delete = Post.objects.first()
        post_to_delete.delete()
        response = self.AUTHOR.get(reverse("posts:index"))
        was_deleted = response.content
        self.assertEqual(not_deleted, was_deleted)


class Testsubunsub(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_a = User.objects.create_user(username="user_a")
        cls.author_p = User.objects.create_user(username="author_p")
        cls.group = Group.objects.create(
            slug=SLUG_1,
            title="test-title",
            description="test-desc",
        )

    def setUp(self):
        self.author = User.objects.create(
            username="test_name",
        )
        self.post = Post.objects.create(
            author=self.author,
            text="Текст, написанный для проверки",
            group=self.group,
        )
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_user_unsub_and_sub(self):
        user2 = User.objects.create_user(username="User2")
        Follow.objects.create(user=self.author_p, author=user2)
        followers_count = Follow.objects.filter(
            user=self.author_p, author=user2
        ).count()
        self.assertEqual(followers_count, 1)
        self.guest_client.get(reverse("posts:profile",
                              kwargs={"username": user2}))
        followers_count = Follow.objects.filter(
            user=self.user_a, author=user2).count()
        self.assertEqual(followers_count, 0)

    def test_follow_post_exists_in_follow_index(self):
        user2 = User.objects.create_user(username="User2")
        post = Post.objects.create(text="Проверка подписки", author=user2)
        Follow.objects.create(user=self.author, author=user2)
        response = self.authorized_client.get(reverse("posts:follow_index"))
        post_text1 = response.context["page_obj"][0].text
        self.assertEqual(post.text, post_text1)

    def test_unfollow_post_does_not_exists_in_follow_index(self):
        user2 = User.objects.create_user(username='User2')
        post = Post.objects.create(text='Проверка подписки', author=user2)
        test_client = Client()
        test_client.force_login(user2)
        Follow.objects.create(user=user2, author=self.author)
        response = test_client.get(reverse("posts:follow_index"))
        post_text1 = response.context['page_obj'][0].text
        self.assertNotEqual(post.text, post_text1)

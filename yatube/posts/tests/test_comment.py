from django.test import TestCase
from django.urls import reverse

from ..models import Comment
from .fixtures import ObjectsCreate, UsersCreate

TEXT = "Some text"


class TestComments(TestCase):
    def setUp(self):

        self.post_author = UsersCreate.author_create()
        self.GUEST = UsersCreate.guest_client_create()
        self.AUTHOR = UsersCreate.authorized_author_client_create()
        self.GROUP = ObjectsCreate.group_create()
        self.POST = ObjectsCreate.post_create(
            self.GROUP, self.post_author, TEXT
        )
        self.comments = reverse("posts:add_comment",
                                kwargs={"post_id": self.POST.id})

    def test_only_logon_user(self):
        response = self.GUEST.get(self.comments)
        self.assertEqual(response.status_code, 302)

    def test_comment_succesfully_added(self):
        comments_count = Comment.objects.count()
        form_data = {"text": "Комментарий к посту"}
        self.AUTHOR.post(
            self.comments,
            data=form_data,
            follow=True,
        )
        Comment.objects.count() == comments_count + 1
        latest_comment = Comment.objects.first()
        self.assertEqual(latest_comment.text, form_data["text"])

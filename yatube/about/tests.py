from django.test import Client, TestCase


class StaticURLTests(TestCase):
    def setUp(self):
        # Устанавливаем данные для тестирования
        # Создаём экземпляр клиента. Он неавторизован.
        self.guest_client = Client()

    def test_homepage(self):
        # Делаем запрос к главной странице и проверяем статус
        response = self.guest_client.get("/")
        # Утверждаем, что для прохождения теста код должен быть равен 200
        self.assertEqual(response.status_code, 200)

    def test_about_author(self):
        self.guest_client = Client()
        response = self.guest_client.get("/about/author/")
        self.assertEqual(response.status_code, 200)

    def test_about_tech(self):
        self.guest_client = Client()
        response = self.guest_client.get("/about/tech/")
        self.assertEqual(response.status_code, 200)

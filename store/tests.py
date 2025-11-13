from django.test import TestCase

# Create your tests here.
from django.urls import reverse

# Create your tests here.
class StoreViewTests(TestCase):
    def test_product_list_page_status_code(self):
        response = self.client.get(reverse('product_list'))
        self.assertEqual(response.status_code, 200)
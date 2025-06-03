from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from inventory.models import ExercisePlan, Category

class ViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )
        self.exercise_plan = ExercisePlan.objects.create(
            name='Test Plan',
            slug='test-plan',
            description='Test Description',
            price=29.99,
            duration_weeks=4,
            difficulty='beginner',
            category=self.category
        )

    def test_home_page(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_exercise_plan_list(self):
        response = self.client.get(reverse('inventory:exercise_plan_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'inventory/exercise_plan_list.html')
        self.assertContains(response, 'Test Plan')

    def test_exercise_plan_detail(self):
        response = self.client.get(reverse('inventory:exercise_plan_detail', args=['test-plan']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'inventory/exercise_plan_detail.html')
        self.assertContains(response, 'Test Plan')

    def test_newsletter_signup(self):
        response = self.client.post(reverse('inventory:newsletter_signup'), {
            'email': 'test@example.com'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful signup

    def test_authenticated_user_access(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('inventory:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'inventory/profile.html')

    def test_unauthenticated_user_redirect(self):
        response = self.client.get(reverse('inventory:profile'))
        self.assertEqual(response.status_code, 302)  # Redirect to login 
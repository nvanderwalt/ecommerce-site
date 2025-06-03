from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from ..models import Category, Product, Review

User = get_user_model()

class ProductCatalogTests(TestCase):
    def setUp(self):
        """Set up test data."""
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
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            description='Test Description',
            price=99.99,
            category=self.category,
            stock=10,
            is_active=True
        )
    
    def test_product_list(self):
        """Test product listing."""
        # Test product list view
        response = self.client.get(reverse('product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'inventory/product_list.html')
        self.assertContains(response, 'Test Product')
        
        # Test category filtering
        response = self.client.get(
            reverse('product_list'),
            {'category': self.category.slug}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Product')
    
    def test_product_detail(self):
        """Test product detail view."""
        response = self.client.get(reverse('product_detail', args=[self.product.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'inventory/product_detail.html')
        self.assertContains(response, 'Test Product')
        self.assertContains(response, 'Test Description')
        self.assertContains(response, '99.99')
    
    def test_product_reviews(self):
        """Test product reviews."""
        # Login first
        self.client.login(username='testuser', password='testpass123')
        
        # Test adding a review
        response = self.client.post(
            reverse('add_review', args=[self.product.slug]),
            {
                'rating': 5,
                'comment': 'Great product!'
            }
        )
        self.assertEqual(response.status_code, 302)  # Redirect after success
        
        # Verify review was created
        review = Review.objects.filter(
            product=self.product,
            user=self.user
        ).first()
        self.assertIsNotNone(review)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, 'Great product!')
    
    def test_product_search(self):
        """Test product search functionality."""
        # Test search with matching term
        response = self.client.get(
            reverse('product_list'),
            {'q': 'Test'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Product')
        
        # Test search with non-matching term
        response = self.client.get(
            reverse('product_list'),
            {'q': 'Nonexistent'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Test Product')
    
    def test_product_filtering(self):
        """Test product filtering."""
        # Create another product with different price
        Product.objects.create(
            name='Expensive Product',
            slug='expensive-product',
            description='Expensive Description',
            price=199.99,
            category=self.category,
            stock=5,
            is_active=True
        )
        
        # Test price range filtering
        response = self.client.get(
            reverse('product_list'),
            {'min_price': 100, 'max_price': 200}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Expensive Product')
        self.assertNotContains(response, 'Test Product')
        
        # Test stock filtering
        response = self.client.get(
            reverse('product_list'),
            {'in_stock': 'on'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Product')
        self.assertContains(response, 'Expensive Product') 
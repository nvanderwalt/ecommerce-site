# FitFusion - Your Complete Fitness Platform

![FitFusion Logo](static/images/logo.png)

## Overview

FitFusion is a comprehensive fitness platform that combines workout plans, nutrition guidance, and community support into one seamless experience. The platform offers both subscription-based services and individual product purchases, creating a complete fusion of fitness resources for users at all levels.

## Table of Contents
1. [User Experience (UX)](#user-experience-ux)
2. [Features](#features)
3. [Technologies Used](#technologies-used)
4. [Testing](#testing)
5. [Deployment](#deployment)
6. [Credits](#credits)
7. [Subscription Renewal System](#subscription-renewal-system)
8. [E-commerce Business Model](#e-commerce-business-model)
9. [Marketing](#marketing)
10. [SEO Implementation](#seo-implementation)

## User Experience (UX)

### User Stories

#### First Time Visitor Goals:
- As a first-time visitor, I want to easily understand the purpose of the site
- As a first-time visitor, I want to be able to navigate the site easily
- As a first-time visitor, I want to view available exercise and nutrition plans

#### Returning Visitor Goals:
- As a returning visitor, I want to track my fitness progress
- As a returning visitor, I want to purchase individual products
- As a returning visitor, I want to subscribe to premium plans

#### Frequent User Goals:
- As a frequent user, I want to interact with the community
- As a frequent user, I want to review products and plans
- As a frequent user, I want to manage my subscription

## Features

### Existing Features
- User Authentication
- Product Catalog
- Exercise Plans
- Nutrition Plans
- User Profiles
- Newsletter Subscription
- Social Media Integration
- SEO Optimization
- Responsive Design
- Shopping Cart System
- Payment Processing (Stripe)
- Subscription Management

### Features Left to Implement
- Advanced progress tracking with charts and analytics
- Mobile app development
- Live streaming workout sessions
- AI-powered workout recommendations

## Responsive Design Showcase

FitFusion is built with a fully responsive design that adapts seamlessly across all devices and screen sizes. The site maintains its professional appearance and functionality whether viewed on desktop, tablet, or mobile devices.

### Desktop View
*The FitFusion homepage on desktop displays the full navigation menu with all features easily accessible. The green navbar spans the full width with clear navigation links, cart functionality, and user authentication options. The content is presented in clean, white boxes with smooth corners on a light gray background.*

### Tablet View
*On tablet devices, the layout adapts to medium screen sizes while maintaining the clean, boxed design with smooth corners. The navigation remains accessible and the content is properly formatted for optimal viewing. The responsive design ensures all elements scale appropriately.*

### Mobile View
*The mobile experience features a hamburger menu for navigation, ensuring all features remain accessible on smaller screens. The content is optimized for touch interaction with appropriate spacing and sizing. The hamburger menu provides easy access to all navigation options.*

### Responsive Features
- **Flexible Navigation**: Hamburger menu on mobile, full menu on desktop
- **Adaptive Layout**: Content boxes that scale appropriately for each screen size
- **Touch-Friendly**: Optimized button sizes and spacing for mobile devices
- **Consistent Branding**: Maintains visual identity across all devices
- **Performance Optimized**: Fast loading times on all connection speeds

## Technologies Used

### Languages Used
- HTML5
- CSS3
- JavaScript
- Python

### Frameworks, Libraries & Programs Used
- Django 5.1.7
- Bootstrap 5.3.2
- SQLite3 (Development)
- PostgreSQL (Production)
- Stripe (Payment Processing)
- Django AllAuth (Authentication)
- Font Awesome 6.4.0 (Icons)
- jQuery (AJAX functionality)

## Testing

### Automated Testing
The project includes automated tests for core functionality:

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test inventory
```

Test coverage includes:
- User authentication
- Exercise plan views
- Newsletter signup
- Protected routes
- Form validation

### Manual Testing
The following features have been manually tested:
- User registration and login
- Exercise plan browsing and filtering
- Shopping cart functionality
- Checkout process
- Newsletter subscription
- Responsive design on different devices

## Deployment

### Prerequisites
- Python 3.8+
- PostgreSQL
- Stripe account
- Email service (for newsletter)

### Environment Variables
Create a `.env` file with the following variables:
```
DEBUG=False
SECRET_KEY=your-secret-key
DATABASE_URL=your-database-url
STRIPE_PUBLIC_KEY=your-stripe-public-key
STRIPE_SECRET_KEY=your-stripe-secret-key
STRIPE_WEBHOOK_SECRET=your-stripe-webhook-secret
EMAIL_HOST=your-email-host
EMAIL_PORT=587
EMAIL_HOST_USER=your-email-user
EMAIL_HOST_PASSWORD=your-email-password
DEFAULT_FROM_EMAIL=your-from-email
```

### Deployment Steps
1. Clone the repository
```bash
git clone https://github.com/yourusername/fitfusion.git
cd fitfusion
```

2. Create and activate virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Set up the database
```bash
python manage.py migrate
```

5. Create superuser
```bash
python manage.py createsuperuser
```

6. Collect static files
```bash
python manage.py collectstatic
```

7. Run the development server
```bash
python manage.py runserver
```

### Production Deployment
For production deployment:
1. Set DEBUG=False in settings.py
2. Configure your web server (e.g., Nginx)
3. Set up SSL certificate
4. Configure your domain
5. Set up database backups
6. Configure error monitoring

## Contact & Support

### Get in Touch
- **🌐 Website:** [FitFusion](https://ecommerce-site-gym-781f127062c6.herokuapp.com/)
- **📘 Facebook:** [FitFusion Facebook Page](https://www.facebook.com/people/FitFusion/61579008766629/)
- **📧 Email:** Contact through the website contact form

### Support
- For technical issues: Check the deployment section above
- For business inquiries: Use the contact form on the website
- For community support: Join our Facebook community

## Credits

### Code
- Django Documentation
- Bootstrap Documentation

### Content
- All content is written by the developer

### Media
- Images will be credited as they are added

### Acknowledgements
- Code Institute for the project requirements and resources
- My Mentor for continuous helpful feedback

## Subscription Renewal System

This project includes an automated subscription renewal system:

- Subscriptions with `auto_renew` enabled will be automatically renewed when they are about to expire.
- The renewal process is handled by a management command: `python manage.py renew_subscriptions`.
- Expired subscriptions are marked as `EXPIRED` and users are notified by email.
- Users can enable or disable auto-renewal from their subscription management page.

### Setting up automatic renewals

To run the renewal process daily, set up a cron job (Linux/macOS) or a scheduled task (Windows) to run:

```
python manage.py renew_subscriptions
```

### Testing the renewal system

Unit tests for the renewal logic are in `subscriptions/tests/test_renewal.py`:

```
python manage.py test subscriptions.tests.test_renewal
```

### Email notifications

- Users receive an email when their subscription is renewed or expired.
- Make sure to configure `DEFAULT_FROM_EMAIL` in your Django settings.

## E-commerce Business Model

### Revenue Streams
1. **Individual Product Sales**
   - Fitness equipment and accessories
   - One-time purchases with immediate delivery
   - Price range: €20-€200 per item

2. **Subscription Services**
   - Monthly/Annual fitness and nutrition plans
   - Premium workout programs with personal coaching
   - Price range: €29.99-€99.99 per month

3. **Premium Content**
   - Exclusive workout videos and tutorials
   - Personalized nutrition guidance
   - Progress tracking and analytics

### Target Market
- **Primary**: Fitness enthusiasts aged 18-45
- **Secondary**: Beginners looking to start their fitness journey
- **Tertiary**: Health-conscious individuals seeking nutrition guidance

### Value Proposition
- Comprehensive fitness solutions in one platform
- Expert-designed workout and nutrition plans
- Community support and progress tracking
- Flexible pricing options for different budgets

### Customer Acquisition Strategy
- Social media marketing (Facebook, Instagram)
- Content marketing through fitness blogs
- Email marketing campaigns
- Referral programs and loyalty rewards

## Marketing

### Social Media Presence

#### Facebook Business Page
FitFusion maintains an active presence on Facebook through our official business page. The page showcases:
- Latest workout plans and nutrition programs
- Success stories from our community
- Fitness tips and health advice
- Special offers and promotions
- Behind-the-scenes content and updates

**🌐 Facebook Business Page:** [FitFusion Facebook Page](https://www.facebook.com/people/FitFusion/61579008766629/)

**📱 Follow us on Facebook for:**
- Daily fitness motivation
- Exclusive workout previews
- Community challenges
- Live Q&A sessions
- Member success stories

*Note: Screenshot of Facebook page will be added once the page is fully set up with content.*

### Newsletter
Users can subscribe to our newsletter to receive:
- Weekly fitness tips
- Exclusive workout plans
- Nutrition advice
- Special offers and promotions

## SEO Implementation

### On-Page SEO
- **Meta Tags**: Comprehensive meta description, keywords, and author tags
- **Title Tags**: Optimized page titles for each section
- **Header Structure**: Proper H1, H2, H3 hierarchy
- **Alt Text**: Descriptive alt attributes for all images
- **Internal Linking**: Strategic internal links between related content

### Technical SEO
- **Sitemap**: XML sitemap for search engine crawling
- **Robots.txt**: Proper robots.txt file for search engine guidance
- **Schema Markup**: Structured data for better search results
- **Mobile Optimization**: Responsive design for mobile-first indexing
- **Page Speed**: Optimized images and CSS for faster loading

### Content SEO
- **Keyword Optimization**: Fitness-related keywords naturally integrated
- **Quality Content**: Comprehensive, valuable content for users
- **Regular Updates**: Fresh content through blog posts and community features
- **User Engagement**: Interactive features to increase time on site

### Local SEO
- **Business Information**: Complete business details in footer
- **Contact Information**: Easy-to-find contact details
- **Social Proof**: Customer testimonials and reviews
- **Social Media Integration**: Links to Facebook Business Page
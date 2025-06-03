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
8. [Marketing](#marketing)

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
- SEO Optimization

### Features Left to Implement
- Community Features
- Subscription System
- Progress Tracking

## Technologies Used

### Languages Used
- HTML5
- CSS3
- JavaScript
- Python

### Frameworks, Libraries & Programs Used
- Django
- Bootstrap
- SQLite3
- Stripe

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

## Marketing

### Facebook Business Page
FitFusion maintains an active presence on Facebook through our business page. The page showcases:
- Latest workout plans and nutrition programs
- Success stories from our community
- Fitness tips and health advice
- Special offers and promotions

![Facebook Business Page](static/images/facebook_page.png)

### Newsletter
Users can subscribe to our newsletter to receive:
- Weekly fitness tips
- Exclusive workout plans
- Nutrition advice
- Special offers and promotions
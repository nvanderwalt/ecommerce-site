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

*Testing documentation will be added as features are implemented.*

## Deployment

*Deployment instructions will be added when the project is ready for production.*

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
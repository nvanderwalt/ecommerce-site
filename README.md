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
- User Profiles

### Features Left to Implement
- Exercise Plans
- Nutrition Plans
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

## Trial Period Feature

The platform includes a 14-day trial period for new users to experience premium features before committing to a paid subscription.

### Trial Period Features

- 14-day free trial for all subscription plans
- Automatic trial expiration
- Email notifications:
  - Trial started confirmation
  - Reminder emails at 3 days and 1 day before trial ends
  - Trial ended notification
- Easy conversion from trial to paid subscription
- One trial per user policy

### Trial Period Workflow

1. **Starting a Trial**
   - Users can start a trial from the subscription plan page
   - Trial period begins immediately upon selection
   - Users receive a welcome email with trial details

2. **During Trial**
   - Full access to premium features
   - Trial status displayed in user dashboard
   - Remaining days shown
   - Option to convert to paid plan at any time

3. **Trial Conversion**
   - Users can convert to paid plan during or after trial
   - Seamless transition through Stripe checkout
   - Maintains access to premium features

4. **Trial Expiration**
   - Automatic expiration after 14 days
   - Email notification sent
   - Option to subscribe to paid plan
   - Special offer for conversion (20% off first month)

### Technical Implementation

- Trial status tracked in `UserSubscription` model
- Email notifications handled by Django's email system
- Stripe integration for trial conversion
- Comprehensive test coverage for all trial features

### Usage Statistics

The platform tracks various metrics related to trial usage:
- Trial conversion rate
- Average time to conversion
- Trial expiration rate
- Feature usage during trial

### Security and Validation

- One trial per user enforced
- Trial status validation on all premium features
- Secure conversion process through Stripe
- Protection against trial abuse
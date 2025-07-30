#!/usr/bin/env python3
"""
Stripe Setup Script for FitFusion
This script helps you configure Stripe keys for the subscription system.
"""

import os
import sys

def main():
    print("🔧 FitFusion Stripe Setup")
    print("=" * 40)
    
    print("\n📋 To get your Stripe keys:")
    print("1. Go to https://stripe.com and create a free account")
    print("2. Go to Dashboard → Developers → API Keys")
    print("3. Copy your test keys (they start with 'pk_test_' and 'sk_test_')")
    
    print("\n🔑 Enter your Stripe keys:")
    
    # Get keys from user
    public_key = input("Public Key (pk_test_...): ").strip()
    secret_key = input("Secret Key (sk_test_...): ").strip()
    
    if not public_key.startswith('pk_test_'):
        print("❌ Invalid public key format. Should start with 'pk_test_'")
        return
    
    if not secret_key.startswith('sk_test_'):
        print("❌ Invalid secret key format. Should start with 'sk_test_'")
        return
    
    # Create .env file content
    env_content = f"""# Stripe Configuration
STRIPE_PUBLIC_KEY={public_key}
STRIPE_SECRET_KEY={secret_key}
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here

# Email Configuration (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
DEFAULT_FROM_EMAIL=noreply@fitfusion.com
"""
    
    # Write to .env file
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("\n✅ .env file created successfully!")
        print("📝 You can now edit the .env file to add your email settings if needed.")
        
        print("\n🚀 Next steps:")
        print("1. Install python-dotenv: pip install python-dotenv")
        print("2. Add 'from dotenv import load_dotenv; load_dotenv()' to your settings.py")
        print("3. Restart your Django server")
        print("4. Test the subscription buttons!")
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")

if __name__ == "__main__":
    main() 
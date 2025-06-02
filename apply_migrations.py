#!/usr/bin/env python
import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'socialmedia.settings')
django.setup()

# Use Django's management commands directly
from django.core.management import call_command

# Apply migrations for the chat app
try:
    call_command('migrate', 'chat')
    print("Successfully applied migrations for the chat app.")
except Exception as e:
    print(f"Error applying migrations: {e}")
    
    # Try applying all migrations as a fallback
    try:
        print("Attempting to apply all migrations...")
        call_command('migrate')
        print("Successfully applied all migrations.")
    except Exception as e:
        print(f"Error applying all migrations: {e}")
        print("\nPlease try running the following command in your virtual environment:")
        print("python manage.py migrate chat")


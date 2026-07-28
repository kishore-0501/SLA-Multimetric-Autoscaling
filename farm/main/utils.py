# utils.py - ready for SQLite use

from django.contrib.auth.models import User

def get_all_users():
    """Return all registered users"""
    return User.objects.all()

def find_user_by_email(email):
    """Find a single user by email"""
    return User.objects.filter(username=email).first()

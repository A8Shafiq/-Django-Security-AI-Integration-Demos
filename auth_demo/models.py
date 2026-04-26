"""
models.py — AppUser model for the SQL Injection Demo

EDUCATIONAL NOTE:
    Passwords are stored in PLAIN TEXT intentionally for this demo.
    In real applications, ALWAYS hash passwords (e.g. Django's make_password).
"""

from django.db import models


class AppUser(models.Model):
    """
    Simple user model for demonstrating SQL Injection.
    NOT for production use — passwords are stored as plain text.
    """
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)  # Plain text for demo only!

    class Meta:
        db_table = 'app_users'  # Explicit table name for raw SQL demos

    def __str__(self):
        return self.username

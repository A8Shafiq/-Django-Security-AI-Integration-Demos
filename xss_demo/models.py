"""
models.py — Comment model for Stored XSS Demo

EDUCATIONAL NOTE:
    This model intentionally stores raw HTML/JS content without sanitization
    to demonstrate Stored XSS attacks. In production, ALWAYS sanitize user input.
"""

from django.db import models


class Comment(models.Model):
    """
    Simple comment model for demonstrating Stored XSS.
    Stores raw user input including any HTML/JS — intentionally unsafe for demo.
    """
    author = models.CharField(max_length=100)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'xss_comments'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.author}: {self.text[:50]}"

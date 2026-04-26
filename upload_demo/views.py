"""
views.py — File Upload Vulnerability Demo Views

Demonstrates how unrestricted file uploads are exploited and how to
defend against them.  Includes detailed terminal logging at every step.

PURPOSE: Educational demonstration of file-upload attacks for developers.
"""

import os
import uuid
import mimetypes

from django.conf import settings
from django.shortcuts import render, redirect

# -----------  constants  -----------
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.pdf', '.txt'}
ALLOWED_MIME_TYPES = {
    'image/jpeg', 'image/png', 'image/gif',
    'application/pdf', 'text/plain',
}
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2 MB


# ---------------------------------------------------
#  DASHBOARD — landing page for File-Upload lab
# ---------------------------------------------------
def upload_dashboard(request):
    """Render the File-Upload demo dashboard."""
    return render(request, 'upload_dashboard.html')


# ===================================================
#  VULNERABLE FILE UPLOAD
# ===================================================
def upload_vulnerable(request):
    """
    [!] INTENTIONALLY VULNERABLE — DO NOT USE IN PRODUCTION [!]

    Accepts ANY file with ZERO validation:
      • No extension check
      • No MIME-type check
      • No file-size limit
      • Original filename kept (path-traversal risk)

    The template shows step-by-step what happened and why it is
    dangerous.
    """
    result = None

    if request.method == 'POST' and request.FILES.get('file'):
        uploaded = request.FILES['file']
        original_name = uploaded.name
        file_size = uploaded.size
        content_type = uploaded.content_type
        extension = os.path.splitext(original_name)[1].lower()

        # ---- Terminal Logging ----
        print("\n" + "=" * 60)
        print("  [VULNERABLE] FILE UPLOAD — New Upload Received")
        print("=" * 60)
        print(f"[STEP 1] Received File")
        print(f"  Filename     : {original_name}")
        print(f"  Extension    : {extension}")
        print(f"  MIME type    : {content_type}")
        print(f"  Size         : {file_size:,} bytes")

        print(f"\n[STEP 2] Validation")
        print(f"  [!!] NO extension check — any file type accepted!")
        print(f"  [!!] NO MIME-type check — Content-Type header ignored!")
        print(f"  [!!] NO size limit — disk exhaustion possible!")
        print(f"  [!!] Original filename preserved — path-traversal possible!")

        # Save to media/uploads_vulnerable/
        save_dir = os.path.join(settings.MEDIA_ROOT, 'uploads_vulnerable')
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, original_name)

        with open(save_path, 'wb+') as dest:
            for chunk in uploaded.chunks():
                dest.write(chunk)

        print(f"\n[STEP 3] File Saved")
        print(f"  Saved to: {save_path}")
        print(f"  [!!] File is accessible and could be executed by the server!")

        # Determine which exploit scenarios apply
        dangers = []
        if extension in ('.php', '.phtml', '.php5', '.phar'):
            dangers.append('web_shell_php')
        if extension in ('.py', '.pyc'):
            dangers.append('web_shell_python')
        if extension in ('.jsp', '.jspx'):
            dangers.append('web_shell_java')
        if extension in ('.exe', '.bat', '.ps1', '.cmd', '.sh'):
            dangers.append('executable')
        if extension in ('.html', '.htm', '.svg'):
            dangers.append('stored_xss')
        if '..' in original_name or '/' in original_name or '\\' in original_name:
            dangers.append('path_traversal')
        if '.' in original_name and original_name.count('.') > 1:
            dangers.append('double_extension')
        if file_size > MAX_FILE_SIZE:
            dangers.append('dos')

        if dangers:
            print(f"\n[STEP 4] [!!] RISKS IDENTIFIED:")
            for d in dangers:
                print(f"  • {d}")
        else:
            print(f"\n[STEP 4] No obvious risk for this particular file, "
                  f"but the lack of validation is still dangerous!")
        print("=" * 60 + "\n")

        result = {
            'filename': original_name,
            'extension': extension,
            'content_type': content_type,
            'size': file_size,
            'size_human': f"{file_size / 1024:.1f} KB" if file_size < 1024 * 1024 else f"{file_size / (1024*1024):.2f} MB",
            'saved_path': save_path,
            'dangers': dangers,
        }

    return render(request, 'upload_vulnerable.html', {'result': result})


# ===================================================
#  SECURE FILE UPLOAD
# ===================================================
def upload_secure(request):
    """
    [SECURE] IMPLEMENTATION — Demonstrates proper file-upload handling.

    Validation steps:
      1. Extension whitelist check
      2. MIME-type whitelist check
      3. File-size cap (2 MB)
      4. Rename file with UUID (prevents path traversal & overwrites)
    """
    result = None

    if request.method == 'POST' and request.FILES.get('file'):
        uploaded = request.FILES['file']
        original_name = uploaded.name
        file_size = uploaded.size
        content_type = uploaded.content_type
        extension = os.path.splitext(original_name)[1].lower()

        print("\n" + "=" * 60)
        print("  [SECURE] FILE UPLOAD — New Upload Received")
        print("=" * 60)
        print(f"[STEP 1] Received File")
        print(f"  Filename     : {original_name}")
        print(f"  Extension    : {extension}")
        print(f"  MIME type    : {content_type}")
        print(f"  Size         : {file_size:,} bytes")

        errors = []

        # Check 1 — Extension whitelist
        print(f"\n[STEP 2] Extension Whitelist Check")
        if extension not in ALLOWED_EXTENSIONS:
            errors.append(f"Extension '{extension}' is not in the whitelist {ALLOWED_EXTENSIONS}")
            print(f"  [BLOCKED] '{extension}' not in allowed list")
        else:
            print(f"  [PASS] '{extension}' is allowed")

        # Check 2 — MIME type whitelist
        print(f"\n[STEP 3] MIME-Type Whitelist Check")
        if content_type not in ALLOWED_MIME_TYPES:
            errors.append(f"MIME type '{content_type}' is not in the whitelist")
            print(f"  [BLOCKED] '{content_type}' not in allowed list")
        else:
            print(f"  [PASS] '{content_type}' is allowed")

        # Check 3 — File size
        print(f"\n[STEP 4] File-Size Check (max {MAX_FILE_SIZE:,} bytes)")
        if file_size > MAX_FILE_SIZE:
            errors.append(f"File size ({file_size:,} bytes) exceeds {MAX_FILE_SIZE:,} byte limit")
            print(f"  [BLOCKED] {file_size:,} > {MAX_FILE_SIZE:,}")
        else:
            print(f"  [PASS] {file_size:,} <= {MAX_FILE_SIZE:,}")

        # Check 4 — Rename with UUID
        safe_name = f"{uuid.uuid4().hex}{extension}"
        print(f"\n[STEP 5] Rename File")
        print(f"  Original : {original_name}")
        print(f"  Renamed  : {safe_name}")
        print(f"  (Prevents path traversal, overwrites, and info leakage)")

        if errors:
            print(f"\n[RESULT] [BLOCKED] Upload rejected:")
            for e in errors:
                print(f"  ✗ {e}")
            print("=" * 60 + "\n")

            result = {
                'accepted': False,
                'filename': original_name,
                'extension': extension,
                'content_type': content_type,
                'size': file_size,
                'size_human': f"{file_size / 1024:.1f} KB" if file_size < 1024 * 1024 else f"{file_size / (1024*1024):.2f} MB",
                'errors': errors,
                'safe_name': safe_name,
            }
        else:
            save_dir = os.path.join(settings.MEDIA_ROOT, 'uploads_secure')
            os.makedirs(save_dir, exist_ok=True)
            save_path = os.path.join(save_dir, safe_name)

            with open(save_path, 'wb+') as dest:
                for chunk in uploaded.chunks():
                    dest.write(chunk)

            print(f"\n[RESULT] [ACCEPTED] File saved securely")
            print(f"  Path: {save_path}")
            print("=" * 60 + "\n")

            result = {
                'accepted': True,
                'filename': original_name,
                'extension': extension,
                'content_type': content_type,
                'size': file_size,
                'size_human': f"{file_size / 1024:.1f} KB" if file_size < 1024 * 1024 else f"{file_size / (1024*1024):.2f} MB",
                'errors': [],
                'safe_name': safe_name,
                'saved_path': save_path,
            }

    return render(request, 'upload_secure.html', {'result': result})


# ===================================================
#  MITIGATIONS REFERENCE
# ===================================================

def mitigations(request):
    """Render the comprehensive mitigations reference page."""
    return render(request, 'mitigations.html')

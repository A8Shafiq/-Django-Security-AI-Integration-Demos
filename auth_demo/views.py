"""
views.py — Vulnerable & Secure Login Views

This file contains TWO login implementations:
  1. vulnerable_login  — uses string concatenation (DANGEROUS!)
  2. secure_login      — uses Django ORM (SAFE)

PURPOSE: Educational demonstration of SQL Injection attacks.
"""

from django.shortcuts import render
from django.db import connection
from .models import AppUser


# ──────────────────────────────────────────────
#  LOGIN PAGE — renders the HTML template
# ──────────────────────────────────────────────
def login_page(request):
    """Render the login page with both forms."""
    return render(request, 'login.html')


# ──────────────────────────────────────────────
#  VULNERABLE LOGIN (DANGEROUS — SQL Injection!)
# ──────────────────────────────────────────────
def vulnerable_login(request):
    """
    ⚠️  INTENTIONALLY VULNERABLE — DO NOT USE IN PRODUCTION ⚠️

    WHY THIS IS DANGEROUS:
        The SQL query is built by directly inserting user input
        into the query string using string concatenation / f-string.
        An attacker can inject arbitrary SQL code through the input fields.

    EXAMPLE ATTACK:
        username: admin
        password: ' OR '1'='1
        This turns the query into:
            SELECT * FROM app_users WHERE username='admin' AND password='' OR '1'='1';
        The OR '1'='1' is always true, so the query returns ALL users,
        and the attacker is logged in without knowing the password.
    """
    if request.method != 'POST':
        return render(request, 'login.html')

    username = request.POST.get('username', '')
    password = request.POST.get('password', '')

    # ---- STEP 1: Log received input ----
    print("\n" + "=" * 60)
    print("  [VULNERABLE] LOGIN ATTEMPT")
    print("=" * 60)
    print(f"[STEP 1] Received Input")
    print(f"  username: {username}")
    print(f"  password: {password}")

    # ---- STEP 2: Build SQL with string concatenation (DANGEROUS!) ----
    # ⚠️  This is the core vulnerability — user input is directly
    #     concatenated into the SQL string with NO sanitization.
    sql_query = (
        f"SELECT * FROM app_users "
        f"WHERE username='{username}' AND password='{password}'"
    )
    print(f"\n[STEP 2] Constructed SQL Query")
    print(f"  {sql_query}")

    # ---- STEP 3: Execute the raw query ----
    print(f"\n[STEP 3] Query Executed")
    try:
        cursor = connection.cursor()
        cursor.execute(sql_query)
        rows = cursor.fetchall()
    except Exception as e:
        print(f"  [ERROR] Database Error: {e}")
        return render(request, 'login.html', {
            'vuln_error': f"Database Error: {e}",
            'vuln_query': sql_query,
        })

    # ---- STEP 4: Log the result ----
    print(f"\n[STEP 4] Result Returned")
    print(f"  Rows returned: {len(rows)}")
    for row in rows:
        print(f"    -> {row}")

    # ---- STEP 5: Authentication decision ----
    if rows:
        if len(rows) > 1:
            msg = "[!!] Authentication BYPASSED -- SQL Injection succeeded!"
            status = "bypassed"
        else:
            msg = "[OK] Login Successful (valid credentials)"
            status = "success"
    else:
        msg = "[X] Login Failed (invalid credentials)"
        status = "failed"

    print(f"\n[STEP 5] {msg}")
    print("=" * 60 + "\n")

    return render(request, 'login.html', {
        'vuln_result': msg,
        'vuln_status': status,
        'vuln_query': sql_query,
        'vuln_rows': len(rows),
        'vuln_username': username,
        'vuln_password': password,
    })


# ──────────────────────────────────────────────
#  SECURE LOGIN (SAFE — uses Django ORM)
# ──────────────────────────────────────────────
def secure_login(request):
    """
    ✅ SECURE IMPLEMENTATION — Safe from SQL Injection

    WHY THIS IS SAFE:
        Django ORM uses parameterized queries internally.
        User input is passed as parameters, NOT concatenated into SQL.
        The database driver treats input as DATA, never as SQL code.

        Even if an attacker types: ' OR '1'='1
        The ORM will search for a user whose password literally equals
        the string  ' OR '1'='1  — which won't match anything.
    """
    if request.method != 'POST':
        return render(request, 'login.html')

    username = request.POST.get('username', '')
    password = request.POST.get('password', '')

    # ---- STEP 1: Log received input ----
    print("\n" + "=" * 60)
    print("  [SECURE] LOGIN ATTEMPT")
    print("=" * 60)
    print(f"[STEP 1] Received Input")
    print(f"  username: {username}")
    print(f"  password: {password}")

    # ---- STEP 2: Show the safe query approach ----
    # Django ORM generates a parameterized query like:
    #   SELECT * FROM app_users WHERE username=%s AND password=%s
    # with parameters: [username, password]
    safe_query_display = (
        f"SELECT * FROM app_users "
        f"WHERE username=%s AND password=%s\n"
        f"  Parameters: ['{username}', '{password}']"
    )
    print(f"\n[STEP 2] Parameterized Query (Safe)")
    print(f"  {safe_query_display}")

    # ---- STEP 3: Execute via Django ORM ----
    print(f"\n[STEP 3] Query Executed (via Django ORM)")
    try:
        user = AppUser.objects.filter(
            username=username,
            password=password
        ).first()
    except Exception as e:
        print(f"  [ERROR] Database Error: {e}")
        return render(request, 'login.html', {
            'sec_error': f"Database Error: {e}",
            'sec_query': safe_query_display,
        })

    # ---- STEP 4: Log the result ----
    print(f"\n[STEP 4] Result Returned")
    if user:
        print(f"  Found user: {user.username}")
    else:
        print(f"  No matching user found")

    # ---- STEP 5: Authentication decision ----
    if user:
        msg = "[OK] Login Successful (valid credentials)"
        status = "success"
    else:
        msg = "[X] Login Failed -- SQL Injection was BLOCKED"
        status = "failed"

    print(f"\n[STEP 5] {msg}")
    print("=" * 60 + "\n")

    return render(request, 'login.html', {
        'sec_result': msg,
        'sec_status': status,
        'sec_query': safe_query_display,
        'sec_username': username,
        'sec_password': password,
    })

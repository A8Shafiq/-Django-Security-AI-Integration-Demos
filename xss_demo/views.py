"""
views.py - XSS Demo Views (Stored, Reflected, DOM-based)

This file contains views demonstrating all 3 types of XSS attacks:
  1. Stored XSS      - malicious script saved in DB, executed on page load
  2. Reflected XSS   - malicious script reflected from URL/query param
  3. DOM-based XSS   - malicious script injected via client-side JS (no server)

Each type has a VULNERABLE and SECURE implementation side-by-side,
with step-by-step terminal logging for educational purposes.

PURPOSE: Educational demonstration of XSS attacks for developers.
"""

from django.shortcuts import render, redirect
from django.utils.html import escape as html_escape
from .models import Comment


# ----------------------------------------------
#  DASHBOARD - landing page for all XSS demos
# ----------------------------------------------
def xss_dashboard(request):
    """Render the XSS demo dashboard with links to all 3 types."""
    return render(request, 'xss_dashboard.html')


# ==============================================
#  1. STORED XSS  (Persistent XSS)
# ==============================================

def stored_xss_vulnerable(request):
    """
    [!] INTENTIONALLY VULNERABLE - DO NOT USE IN PRODUCTION [!]

    HOW IT WORKS:
        1. Attacker submits a comment containing <script>alert('XSS')</script>
        2. The comment is saved to the database AS-IS (no sanitization)
        3. When ANY user views the page, the template renders the comment
           using the |safe filter, which tells Django NOT to escape HTML
        4. The browser executes the script - XSS attack succeeds!

    WHY THIS IS DANGEROUS:
        Every visitor to the comments page will have the malicious
        script execute in THEIR browser. The attacker only needs to
        submit once, and the attack persists forever in the database.
    """
    if request.method == 'POST':
        author = request.POST.get('author', '')
        text = request.POST.get('text', '')

        # ---- Terminal Logging ----
        print("\n" + "=" * 60)
        print("  [VULNERABLE] STORED XSS - New Comment Submitted")
        print("=" * 60)
        print(f"[STEP 1] Received Input")
        print(f"  Author : {author}")
        print(f"  Comment: {text}")

        print(f"\n[STEP 2] Saving to Database")
        print(f"  [!!] Raw HTML/JS stored WITHOUT any sanitization!")
        print(f"  INSERT INTO xss_comments (author, text) VALUES ('{author}', '{text}')")

        Comment.objects.create(author=author, text=text)
        print(f"  [OK] Comment saved to database")

        print(f"\n[STEP 3] Rendering Template")
        print(f"  Using |safe filter -> browser WILL execute any <script> tags")
        print(f"  Malicious code: {text}")

        if '<script' in text.lower() or 'onerror' in text.lower() or 'onload' in text.lower():
            print(f"\n[STEP 4] [!!] ATTACK DETECTED - Script will run in victim's browser!")
            print(f"  Attack type : Stored (Persistent) XSS")
            print(f"  Impact      : Every visitor will execute this script")
            print(f"  Persistence : Stored in database forever until removed")
        else:
            print(f"\n[STEP 4] Comment appears safe (no obvious script tags)")

        print("=" * 60 + "\n")
        return redirect('xss_demo:stored_vuln')

    comments = Comment.objects.all()

    print("\n" + "-" * 60)
    print("  [VULNERABLE] STORED XSS - Page Loaded")
    print("-" * 60)
    print(f"  Loading {comments.count()} comments from database")
    print(f"  Rendering with |safe filter (NO escaping)")
    for c in comments:
        if '<script' in c.text.lower() or 'onerror' in c.text.lower():
            print(f"  [!!] MALICIOUS: {c.author} -> {c.text}")
        else:
            print(f"  [OK] Safe: {c.author} -> {c.text}")
    print("-" * 60 + "\n")

    return render(request, 'stored_xss.html', {
        'comments': comments,
        'mode': 'vulnerable',
    })


def stored_xss_secure(request):
    """
    [SECURE] IMPLEMENTATION - Safe from Stored XSS

    WHY THIS IS SAFE:
        Django's template engine AUTO-ESCAPES all variables by default.
        When we render {{ comment.text }} without |safe, Django converts:
            <script>  ->  &lt;script&gt;
            "         ->  &quot;
            '         ->  &#x27;
        The browser displays the text literally instead of executing it.
    """
    if request.method == 'POST':
        author = request.POST.get('author', '')
        text = request.POST.get('text', '')

        # ---- Terminal Logging ----
        print("\n" + "=" * 60)
        print("  [SECURE] STORED XSS - New Comment Submitted")
        print("=" * 60)
        print(f"[STEP 1] Received Input")
        print(f"  Author : {author}")
        print(f"  Comment: {text}")

        print(f"\n[STEP 2] Saving to Database")
        print(f"  Raw input stored (Django ORM handles parameterization)")

        Comment.objects.create(author=author, text=text)
        print(f"  [OK] Comment saved to database")

        print(f"\n[STEP 3] Rendering Template")
        print(f"  Using Django auto-escaping (NO |safe filter)")
        print(f"  Original : {text}")
        print(f"  Escaped  : {html_escape(text)}")

        print(f"\n[STEP 4] [SAFE] ATTACK BLOCKED - Script rendered as plain text")
        print(f"  Django auto-escape converts < > \" ' & to HTML entities")
        print(f"  Browser displays the text literally, does NOT execute it")
        print("=" * 60 + "\n")
        return redirect('xss_demo:stored_secure')

    comments = Comment.objects.all()

    print("\n" + "-" * 60)
    print("  [SECURE] STORED XSS - Page Loaded")
    print("-" * 60)
    print(f"  Loading {comments.count()} comments from database")
    print(f"  Rendering with auto-escaping (ALL HTML entities escaped)")
    for c in comments:
        print(f"  [OK] Escaped: {c.author} -> {html_escape(c.text)}")
    print("-" * 60 + "\n")

    return render(request, 'stored_xss.html', {
        'comments': comments,
        'mode': 'secure',
    })


# ==============================================
#  2. REFLECTED XSS  (Non-Persistent XSS)
# ==============================================

def reflected_xss_vulnerable(request):
    """
    [!] INTENTIONALLY VULNERABLE - DO NOT USE IN PRODUCTION [!]

    HOW IT WORKS:
        1. User searches for something via GET ?q=<payload>
        2. The server echoes the search query back in the response
        3. If the template uses |safe, the browser executes any HTML/JS
        4. Attacker sends victim a crafted URL like:
           /xss/reflected/vulnerable/?q=<script>alert('XSS')</script>

    WHY THIS IS DANGEROUS:
        The attack is delivered via URL - attacker sends the link
        to the victim (via email, chat, etc.). When victim clicks,
        the script runs in their browser session.
    """
    query = request.GET.get('q', '')

    if query:
        print("\n" + "=" * 60)
        print("  [VULNERABLE] REFLECTED XSS - Search Request")
        print("=" * 60)
        print(f"[STEP 1] Received Search Query from URL")
        print(f"  GET parameter q = {query}")
        print(f"  Full URL: {request.build_absolute_uri()}")

        print(f"\n[STEP 2] Processing Query")
        print(f"  [!!] No input validation or sanitization applied!")
        print(f"  Raw query passed directly to template")

        print(f"\n[STEP 3] Rendering Template")
        print(f"  Using |safe filter -> browser WILL execute any scripts")
        print(f"  Rendered output: {query}")

        if '<script' in query.lower() or 'onerror' in query.lower() or 'onload' in query.lower():
            print(f"\n[STEP 4] [!!] ATTACK DETECTED - Script reflected back to victim!")
            print(f"  Attack type   : Reflected (Non-Persistent) XSS")
            print(f"  Attack vector : Malicious URL sent to victim")
            print(f"  Impact        : Script executes in victim's browser session")
            print(f"  Persistence   : One-time (only when victim clicks the link)")
        else:
            print(f"\n[STEP 4] Query appears safe (no obvious script tags)")

        print("=" * 60 + "\n")

    return render(request, 'reflected_xss.html', {
        'query': query,
        'mode': 'vulnerable',
    })


def reflected_xss_secure(request):
    """
    [SECURE] IMPLEMENTATION - Safe from Reflected XSS

    WHY THIS IS SAFE:
        Django auto-escapes {{ query }} in templates.
        Even if the URL contains <script>alert('XSS')</script>,
        it will be rendered as &lt;script&gt;alert(&#x27;XSS&#x27;)&lt;/script&gt;
        - visible as text, NOT executable.
    """
    query = request.GET.get('q', '')

    if query:
        print("\n" + "=" * 60)
        print("  [SECURE] REFLECTED XSS - Search Request")
        print("=" * 60)
        print(f"[STEP 1] Received Search Query from URL")
        print(f"  GET parameter q = {query}")

        print(f"\n[STEP 2] Processing Query")
        print(f"  Input will be auto-escaped by Django template engine")

        print(f"\n[STEP 3] Rendering Template")
        print(f"  Using Django auto-escaping (NO |safe filter)")
        print(f"  Original : {query}")
        print(f"  Escaped  : {html_escape(query)}")

        print(f"\n[STEP 4] [SAFE] ATTACK BLOCKED - Script rendered as plain text")
        print(f"  < > \" ' & converted to HTML entities")
        print(f"  Browser displays text literally, does NOT execute it")
        print("=" * 60 + "\n")

    return render(request, 'reflected_xss.html', {
        'query': query,
        'mode': 'secure',
    })


# ==============================================
#  3. DOM-BASED XSS  (Client-Side XSS)
# ==============================================

def dom_xss(request):
    """
    DOM-based XSS Demo - Entirely Client-Side

    HOW IT WORKS:
        This type of XSS happens entirely in the browser (no server involved).

        VULNERABLE VERSION:
        1. JavaScript reads user input from location.hash (URL fragment)
        2. It writes the value into the page using innerHTML
        3. If the hash contains <img src=x onerror=alert('XSS')>,
           the browser parses and executes it

        SECURE VERSION:
        1. JavaScript reads user input from location.hash
        2. It writes the value using textContent (NOT innerHTML)
        3. The browser treats it as plain text - no execution

    ATTACK EXAMPLE:
        URL: /xss/dom/#<img src=x onerror=alert('XSS')>
    """
    print("\n" + "=" * 60)
    print("  [INFO] DOM-BASED XSS - Page Loaded")
    print("=" * 60)
    print("[STEP 1] Server renders the page template")
    print("  The XSS vulnerability is entirely CLIENT-SIDE")
    print("  No malicious data passes through the server")

    print(f"\n[STEP 2] How the attack works:")
    print(f"  1. Attacker crafts URL with malicious hash fragment:")
    print(f"     /xss/dom/#<img src=x onerror=alert('XSS')>")
    print(f"  2. Victim opens the link in their browser")
    print(f"  3. JavaScript reads location.hash")
    print(f"  4. VULNERABLE: innerHTML parses and executes the HTML")
    print(f"     SECURE: textContent displays it as plain text")

    print(f"\n[STEP 3] Key difference:")
    print(f"  element.innerHTML = userInput   -> [!!] DANGEROUS (parses HTML)")
    print(f"  element.textContent = userInput  -> [OK] SAFE (plain text only)")
    print("=" * 60 + "\n")

    return render(request, 'dom_xss.html')

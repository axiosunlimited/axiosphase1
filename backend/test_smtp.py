#!/usr/bin/env python
import os
import sys
import ssl
import certifi

print("=== SSL Configuration Diagnostics ===")
print(f"Python SSL version: {ssl.OPENSSL_VERSION}")
print(f"SSL default verify paths: {ssl.get_default_verify_paths()}")
print(f"Certifi bundle location: {certifi.where()}")
print(f"SSL_CERT_FILE env: {os.environ.get('SSL_CERT_FILE', 'Not set')}")
print(f"REQUESTS_CA_BUNDLE env: {os.environ.get('REQUESTS_CA_BUNDLE', 'Not set')}")
print("")

# Check if certificate files exist
import os.path
cert_paths = [
    "/etc/ssl/certs/ca-certificates.crt",
    certifi.where(),
]

for path in cert_paths:
    exists = os.path.exists(path)
    size = os.path.getsize(path) if exists else 0
    print(f"{path}: {'EXISTS' if exists else 'MISSING'} ({size} bytes)")

print("\n=== Testing SMTP with different SSL contexts ===")

import smtplib
from email.mime.text import MIMEText

smtp_host = "smtp.gmail.com"
smtp_port = 587
smtp_user = os.environ.get("EMAIL_HOST_USER", "")
smtp_password = os.environ.get("EMAIL_HOST_PASSWORD", "")

# Test 1: Default SSL context
print("\n1. Testing with default SSL context...")
try:
    server = smtplib.SMTP(smtp_host, smtp_port, timeout=10)
    server.starttls()
    server.login(smtp_user, smtp_password)
    print("✓ SUCCESS with default context")
    server.quit()
except Exception as e:
    print(f"✗ FAILED: {e}")

# Test 2: SSL context with certifi bundle
print("\n2. Testing with certifi bundle...")
try:
    context = ssl.create_default_context(cafile=certifi.where())
    server = smtplib.SMTP(smtp_host, smtp_port, timeout=10)
    server.starttls(context=context)
    server.login(smtp_user, smtp_password)
    print("✓ SUCCESS with certifi bundle")
    server.quit()
except Exception as e:
    print(f"✗ FAILED: {e}")

# Test 3: SSL context with system certs
print("\n3. Testing with system ca-certificates.crt...")
try:
    context = ssl.create_default_context(cafile="/etc/ssl/certs/ca-certificates.crt")
    server = smtplib.SMTP(smtp_host, smtp_port, timeout=10)
    server.starttls(context=context)
    server.login(smtp_user, smtp_password)
    print("✓ SUCCESS with system certs")
    server.quit()
except Exception as e:
    print(f"✗ FAILED: {e}")

# Test 4: Unverified SSL (insecure, for comparison)
print("\n4. Testing with unverified SSL (insecure)...")
try:
    context = ssl._create_unverified_context()
    server = smtplib.SMTP(smtp_host, smtp_port, timeout=10)
    server.starttls(context=context)
    server.login(smtp_user, smtp_password)
    print("✓ SUCCESS with unverified context (insecure)")
    server.quit()
except Exception as e:
    print(f"✗ FAILED: {e}")

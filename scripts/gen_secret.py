#!/usr/bin/env python
"""Generate a strong random Flask SECRET_KEY and admin password hash helper."""
from secrets import token_hex
from werkzeug.security import generate_password_hash
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--admin-password', help='Optional plain admin password to hash (printed).')
args = parser.parse_args()

secret = token_hex(32)
print(f"SECRET_KEY={secret}")
if args.admin_password:
    print(f"ADMIN_PASSWORD_HASH={generate_password_hash(args.admin_password)}")
else:
    print("(Geef --admin-password om ook een hash te genereren)")

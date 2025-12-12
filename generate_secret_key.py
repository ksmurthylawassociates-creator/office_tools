"""
Quick script to generate a secure SECRET_KEY for production deployment.
Run this before deploying to get a secure random key.
"""
import secrets

if __name__ == "__main__":
    secret_key = secrets.token_hex(32)
    print("\n" + "="*60)
    print("Generated SECRET_KEY for production:")
    print("="*60)
    print(secret_key)
    print("="*60)
    print("\nCopy this key and use it as your SECRET_KEY environment variable.")
    print("Example: SECRET_KEY=" + secret_key)
    print("\n")


"""
Project Astra - Main Application Entrypoint
Day 1: Basic setup and architecture initialization.
"""

from app.config import settings

def main():
    print(f"[{settings.APP_NAME}] Initializing...")
    print("Hello AI")

if __name__ == "__main__":
    main()

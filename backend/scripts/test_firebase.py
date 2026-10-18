"""Quick verification script for Google Firebase Firestore connectivity.

Usage:
    python backend/scripts/test_firebase.py
    python backend/scripts/test_firebase.py --credentials backend/data/serviceAccountKey.json
"""
import argparse
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.repositories.firestore import get_firestore_client, resolve_credentials_path


def main():
    parser = argparse.ArgumentParser(description="Test Firebase Firestore connection")
    parser.add_argument(
        "--credentials",
        type=str,
        default=None,
        help="Path to Firebase service account JSON",
    )
    args = parser.parse_args()

    print("[*] Probing Firebase Credentials...")
    cred_path = resolve_credentials_path(args.credentials)
    if cred_path:
        print(f"    [+] Credentials file found: {cred_path}")
    else:
        print("    [!] No serviceAccountKey.json found at default locations:")
        print("        - backend/data/serviceAccountKey.json")
        print("        - backend/serviceAccountKey.json")
        print("        - FIREBASE_CREDENTIALS_PATH environment variable")

    print("[*] Attempting connection to Firestore...")
    try:
        client = get_firestore_client(credentials_path=args.credentials)
        project_id = getattr(client, "project", "Connected")
        print(f"    [+] Successfully connected to Firestore (Project: {project_id})!")
        
        # Test collection read
        collections = list(client.collections())
        col_names = [c.id for c in collections]
        print(f"    [+] Existing Collections ({len(col_names)}): {', '.join(col_names) if col_names else 'None (Empty Database)'}")
        print("\n[SUCCESS] Your Firebase Firestore setup is ready for seeding!")
        print("Run the following command to populate all collections:")
        print("    python -m app.core.seeder --firebase")
    except Exception as e:
        print(f"\n[-] Firestore Connection Failed: {e}")
        print("\n[GUIDE] To configure Firebase:")
        print("1. Go to Firebase Console -> Project Settings -> Service Accounts")
        print("2. Click 'Generate new private key' (downloads JSON file)")
        print("3. Rename the file to 'serviceAccountKey.json' and place it in 'backend/data/'")
        print("4. Re-run this script to verify!")
        sys.exit(1)


if __name__ == "__main__":
    main()

import os
import json
import requests
import firebase_admin
from firebase_admin import credentials, messaging

def init_firebase():
    if not firebase_admin._apps:
        # 1. First preference: Read direct JSON string from GitHub Secrets
        service_account_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
        
        if service_account_json:
            try:
                cred_dict = json.loads(service_account_json)
                
                # Fix escaped newlines in private key if any
                if "private_key" in cred_dict:
                    cred_dict["private_key"] = cred_dict["private_key"].replace("\\n", "\n")
                    
                cred = credentials.Certificate(cred_dict)
                firebase_admin.initialize_app(cred)
                print("✅ Firebase initialized via Environment Variable Secret!")
                return True
            except Exception as e:
                print(f"❌ Error parsing FIREBASE_SERVICE_ACCOUNT_JSON: {e}")

        # 2. Fallback: Read local JSON file
        cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase_credentials.json")
        if os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            print("✅ Firebase initialized via Local Credentials File!")
            return True
        else:
            print("❌ Firebase credentials missing!")
            return False
            
    return True

import os
import requests
import firebase_admin
from firebase_admin import credentials, messaging

# 1. Firebase Admin SDK Initialize
def init_firebase():
    if not firebase_admin._apps:
        # GitHub Secrets मधून किंवा फाईल मधून Credential लोड करणे
        cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase_credentials.json")
        if os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            return True
        else:
            print("❌ Firebase credentials file not found!")
            return False
    return True

def process_and_send_forum_notifications():
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY") # Service Role Key or Anon Key

    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Supabase Credentials missing!")
        return

    if not init_firebase():
        return

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }

    # अ) प्रलंबित (is_read = false) नोटीफिकेशन्स फेच करा
    url = f"{SUPABASE_URL}/rest/v1/forum_notifications?select=id,user_id,title,body,post_id&is_read=eq.false"
    res = requests.get(url, headers=headers)

    if res.status_code != 200 or not res.json():
        print("ℹ️ काहीही प्रलंबित (Pending) फोरम नोटीफिकेशन्स नाहीत.")
        return

    notifications = res.json()
    print(f"🔔 एकूण {len(notifications)} प्रलंबित नोटीफिकेशन्स सापडली.")

    for item in notifications:
        target_user_id = item.get("user_id")
        
        # ब) target_user_id साठी push_tokens मधून FCM टोकन आणा
        token_url = f"{SUPABASE_URL}/rest/v1/push_tokens?user_id=eq.{target_user_id}&select=token"
        token_res = requests.get(token_url, headers=headers)
        
        if token_res.status_code == 200 and token_res.json():
            tokens = [t["token"] for t in token_res.json() if t.get("token")]
            
            for token in tokens:
                try:
                    # क) Firebase Admin SDK द्वारे १-टू-१ पुश मेसेज
                    message = messaging.Message(
                        notification=messaging.Notification(
                            title=item.get("title", "💬 फोरम अपडेट"),
                            body=item.get("body", "")
                        ),
                        data={
                            "title": item.get("title", ""),
                            "body": item.get("body", ""),
                            "post_id": str(item.get("post_id", "")),
                            "click_action": "OPEN_FORUM_QUESTION"
                        },
                        token=token
                    )
                    response = messaging.send(message)
                    print(f"✅ Push Notification Sent to User {target_user_id}: {response}")
                except Exception as e:
                    print(f"❌ FCM Push Error: {e}")

            # ड) पाठवून झाल्यावर स्टेटस अपडेट करा (is_read = true)
            update_url = f"{SUPABASE_URL}/rest/v1/forum_notifications?id=eq.{item['id']}"
            requests.patch(update_url, headers=headers, json={"is_read": True})

if __name__ == "__main__":
    process_and_send_forum_notifications()

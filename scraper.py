import os
import json
import re
import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client
import firebase_admin
from firebase_admin import credentials, messaging

# Firebase Admin SDK इनिशिअलाइज करणे
def init_firebase_admin():
    try:
        if not firebase_admin._apps:
            # लोकल किंवा GitHub Actions मधील environment variable मधून credentials घेणे
            cred_json_str = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
            if cred_json_str:
                cred_dict = json.loads(cred_json_str)
                cred = credentials.Certificate(cred_dict)
            else:
                # लोकल टेस्टसाठी फाईलवरून घेणे
                cred = credentials.Certificate("firebase_credentials.json")
            firebase_admin.initialize_app(cred)
    except Exception as e:
        print(f"⚠️ Firebase Admin initialization error: {e}")

def send_push_notification_for_new_job(job_title, job_url):
    print("🚀 Triggering Instant FCM Push Notification using Firebase Admin SDK...")
    
    SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

    if not SUPABASE_URL or not SUPABASE_KEY:
        print("⚠️ Supabase credentials missing. Skipping push notification.")
        return

    try:
        # Firebase Admin SDK चालू करणे
        init_firebase_admin()
        
        # Supabase मधून सर्व युझर्सचे FCM टॉकेन्स घेणे
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        response = supabase.table("push_tokens").select("token").execute()
        tokens_data = response.data

        if not tokens_data:
            print("⚠️ No push tokens registered in Supabase.")
            return

        tokens = [item["token"] for item in tokens_data if item.get("token")]
        print(f"📱 Broadcasting notification to {len(tokens)} registered devices...")

        # Firebase Admin Messaging द्वारे बल्क मेसेज पाठवणे (Multicast)
        # Firebase एकाच वेळी शेकडो टॉकेन्सना हाय-प्रायोरिटी मेसेज पाठवू शकते
        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title="🎯 नवीन शासकीय नोकरी अपडेट!",
                body=f"{job_title} - सविस्तर पाहण्यासाठी क्लिक करा."
            ),
            data={
                "title": job_title,
                "official_url": job_url,
                "open_deep_link": "true"
            },
            tokens=tokens,
            android=messaging.AndroidConfig(
                priority="high",
                notification=messaging.AndroidNotification(
                    sound="default",
                    click_action="OPEN_JOB_DETAILS"
                )
            )
        )

        response_fcm = messaging.send_each_for_multicast(message)
        print(f"✅ Successfully sent message to {response_fcm.success_count} devices.")
        if response_fcm.failure_count > 0:
            print(f"⚠️ Failed for {response_fcm.failure_count} tokens.")

    except Exception as e:
        print(f"❌ Error broadcasting push notification via Admin SDK: {e}")

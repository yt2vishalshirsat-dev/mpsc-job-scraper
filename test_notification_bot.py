import os
import requests
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
FCM_SERVER_KEY = os.getenv("FCM_SERVER_KEY", "")

def send_push_notification():
    print("🚀 Fetching push tokens from Supabase...")
    
    try:
        # Supabase क्लायंट कनेक्ट करणे
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # 'push_tokens' टेबलमधून सर्व रजिस्टर्ड टॉकेन्स फेच करणे
        response = supabase.table("push_tokens").select("token").execute()
        tokens_data = response.data
        
        if not tokens_data:
            print("❌ No push tokens found in Supabase table 'push_tokens'! Please open the app once to register token.")
            return
            
        tokens = [item["token"] for item in tokens_data if item.get("token")]
        print(f"📱 Found {len(tokens)} active device tokens.")
        
        # FCM HTTP v1 किंवा 레गसी API द्वारे प्रत्येक डिव्हाइसला पाठवणे
        fcm_url = "https://fcm.googleapis.com/fcm/send"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"key={FCM_SERVER_KEY}"
        }
        
        for token in tokens:
            payload = {
                "to": token,  # थेट वैयक्तिक डिव्हाइस टोकन
                "priority": "high",
                "notification": {
                    "title": "🎯 MPSC लिपिक-टंकलेखक भरती २०२६",
                    "body": "नवीन नोकरीची माहिती आली आहे! सविस्तर पाहण्यासाठी क्लिक करा.",
                    "click_action": "OPEN_JOB_DETAILS"
                },
                "data": {
                    "job_id": "test_job_999",
                    "title": "🎯 MPSC लिपिक-टंकलेखक भरती २०२६",
                    "official_url": "https://www.google.com/search?q=MPSC+Clerk+Typist+Recruitment+2026",
                    "open_deep_link": "true"
                }
            }
            
            res = requests.post(fcm_url, headers=headers, json=payload, timeout=10)
            if res.status_code == 200:
                print(f"✅ Notification sent successfully to token: {token[:15]}...")
            else:
                print(f"❌ Failed for token. Response: {res.text}")
                
    except Exception as e:
        print(f"❌ Error in notification script: {e}")

if __name__ == "__main__":
    send_push_notification()

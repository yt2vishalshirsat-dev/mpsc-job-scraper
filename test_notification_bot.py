import os
import requests
import json

# Firebase Cloud Messaging (FCM) v1 API किंवा Server Key द्वारे
# तुम्हाला FCM / OneSignal / Custom Push Service वापरता येईल.
# इथे आपण FCM HTTP v1 / Legacy Endpoint साठी पेलोड स्ट्रक्चर बनवत आहोत.

FCM_SERVER_KEY = os.getenv("FCM_SERVER_KEY", "")

# 🎯 टेस्टसाठी फेक जॉब डेटा जो ॲपमध्ये हायलाइट होईल
FAKE_JOB_DATA = {
    "job_id": "test_job_999",
    "title": "🎯 MPSC लिपिक-टंकलेखक आणि कर सहाय्यक भरती २०२६",
    "department": "महाराष्ट्र लोकसेवा आयोग (MPSC)",
    "last_date": "30/10/2026",
    "qualification": "Graduate / Any Degree",
    "official_url": "https://www.google.com/search?q=MPSC+Clerk+Typist+Recruitment+2026",
    "is_highlighted": True
}

def send_push_notification():
    print("🚀 Sending Test Notification from GitHub Actions...")
    
    # टॉपिक 'all_job_seekers' ला सबस्क्राईब केलेल्या सर्व ॲप्सना ही नोटीफिकेशन जाईल
    fcm_url = "https://fcm.googleapis.com/fcm/send"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"key={FCM_SERVER_KEY}"
    }
    
    # 📱 deep link intent payload
    payload = {
        "to": "/topics/all_job_seekers",
        "priority": "high",
        "notification": {
            "title": FAKE_JOB_DATA["title"],
            "body": f"स्थान: महाराष्ट्र | शेवटची तारीख: {FAKE_JOB_DATA['last_date']} | सविस्तर पाहण्यासाठी क्लिक करा!",
            "click_action": "OPEN_JOB_DETAILS"
        },
        "data": {
            "job_id": FAKE_JOB_DATA["job_id"],
            "title": FAKE_JOB_DATA["title"],
            "department": FAKE_JOB_DATA["department"],
            "official_url": FAKE_JOB_DATA["official_url"],
            "open_deep_link": "true"
        }
    }

    try:
        response = requests.post(fcm_url, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            print("✅ Test Notification Sent Successfully to App!")
            print(f"🔗 Attached Target Link: {FAKE_JOB_DATA['official_url']}")
        else:
            print(f"❌ Failed to send notification. Status: {response.status_code}, Details: {response.text}")
    except Exception as e:
        print(f"❌ Error sending FCM notification: {e}")

if __name__ == "__main__":
    send_push_notification()

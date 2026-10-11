import time
import random
import datetime
import requests

# १. वेळेची अट (7 AM to 10 PM IST)
def is_within_active_hours():
    # UTC to IST (+5:30)
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    ist_now = now_utc + datetime.timedelta(hours=5, minutes=30)
    current_hour = ist_now.hour
    
    # 7 AM (7) ते 10 PM (22)
    return 7 <= current_hour < 22

# २. प्रश्नांचा साठा (MPSC / ZP / Marathi Grammar Questions Pool)
QUESTION_POOL = [
    {"title": "महाराष्ट्रातील सर्वात लांब नदी कोणती आहे?", "category": "भूगोल"},
    {"title": "MPSC Combined prelims साठी चालू घडामोडीचे किती महिन्यांचे रीडिंग पुरेसे आहे?", "category": "MPSC"},
    {"title": "मराठी व्याकरणातील 'प्रयोग' घटकावर सोपे नोट्स मिळतील का?", "category": "मराठी"},
    {"title": "अहिल्यानगर जिल्ह्याची स्थापना कधी झाली?", "category": "सामान्य ज्ञान"},
    {"title": "तलाठी भरतीसाठी गणिताचा सरावासाठी कोणते पुस्तक उत्तम आहे?", "category": "गणिते & बुद्धिमत्ता"},
    {"title": "भारतीय राज्यघटनेतील कलम ३७० कशाशी संबंधित होते?", "category": "राज्यशास्त्र"},
    {"title": "MPSC राज्यसेवा मुख्य परीक्षेचा नवीन पॅटर्न कधीपासून लागू होत आहे?", "category": "MPSC Updates"},
    {"title": "इंग्रजी Grammar मधील Tenses चे सोपे नियम कोणी सांगू शकेल का?", "category": "English"}
]

# ३. फेक युझर प्रोफाइल नेम (रिअल वाटण्यासाठी)
BOT_USERS = [
    {"user_id": "bot_user_101", "user_name": "सचिन पाटील"},
    {"user_id": "bot_user_102", "user_name": "स्नेहल जगताप"},
    {"user_id": "bot_user_103", "user_name": "राहुल शिंदे"},
    {"user_id": "bot_user_104", "user_name": "पूजा देशमुख"},
    {"user_id": "bot_user_105", "user_name": "अमित पवार"}
]

def post_question_to_forum(question_data, user_data):
    """ तुमच्या सध्याच्या फोरम API / Firebase वर प्रश्न पोस्ट करण्याचे काम करेल """
    
    # तुमच्या रिअल API किंवा Firebase Endpoint ची URL
    FORUM_API_URL = "https://your-app-api.com/api/forum/post_question" 
    
    payload = {
        "user_id": user_data["user_id"],
        "user_name": user_data["user_name"],
        "question_title": question_data["title"],
        "category": question_data["category"],
        "timestamp": int(time.time()),
        "upvotes": 0,
        "is_bot": True # ओळखीसाठी फ्लॅग ठेवू शकता
    }
    
    try:
        response = requests.post(FORUM_API_URL, json=payload, timeout=10)
        if response.status_code in [200, 201]:
            print(f" Successfully posted: '{question_data['title']}' by {user_data['user_name']}")
        else:
            print(f" Failed to post. Status: {response.status_code}")
    except Exception as e:
        print(f" Error posting question: {e}")

def main():
    if not is_within_active_hours():
        print(" Outside active hours (7 AM - 10 PM IST). Skipping execution.")
        return

    print(" Within Active Hours! Preparing 2 random posts for this hour...")
    
    # या तासात २ प्रश्न पोस्ट करणे
    for i in range(2):
        # १ ते २० मिनिटांचा रँडम डिले (Random delay between 1 to 20 minutes)
        delay_seconds = random.randint(60, 1200)
        print(f" Waiting for {delay_seconds // 60} minutes and {delay_seconds % 60} seconds before Question {i+1}...")
        time.sleep(delay_seconds)
        
        # रँडम प्रश्न आणि युझर निवडणे
        selected_question = random.choice(QUESTION_POOL)
        selected_user = random.choice(BOT_USERS)
        
        post_question_to_forum(selected_question, selected_user)

if __name__ == "__main__":
    main()

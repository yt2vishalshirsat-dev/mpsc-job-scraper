import os
import time
import random
import datetime
from supabase import create_client, Client

def is_within_active_hours():
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    ist_now = now_utc + datetime.timedelta(hours=5, minutes=30)
    current_hour = ist_now.hour
    return 7 <= current_hour < 22

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

QUESTION_POOL = [
    {"title": "MPSC Combined पूर्व परीक्षेसाठी चालू घडामोडीचे किती महिन्यांचे रीडिंग पुरेसे आहे?", "category": "MPSC"},
    {"title": "महाराष्ट्रातील सर्वात मोठी नदी कोणती आणि तिची एकूण लांबी किती आहे?", "category": "भूगोल"},
    {"title": "मराठी व्याकरणातील 'प्रयोग' या घटकावर सोप्या ट्रिक्स किंवा नोट्स मिळतील का?", "category": "मराठी"},
    {"title": "अहिल्यानगर (अहमदनगर) जिल्ह्याचे नवीन नामांतर अधिकृतपणे कधी लागू झाले?", "category": "सामान्य ज्ञान"},
    {"title": "तलाठी आणि ZP भरतीसाठी गणिताच्या सरावासाठी कोणते पुस्तक सर्वोत्तम आहे?", "category": "गणिते & बुद्धिमत्ता"},
    {"title": "भारतीय राज्यघटनेतील कलम ३७० कशाशी संबंधित होते?", "category": "राज्यशास्त्र"},
    {"title": "MPSC राज्यसेवा मुख्य परीक्षेचा नवीन डिस्क्रिप्टिव्ह पॅटर्न कधीपासून लागू होत आहे?", "category": "MPSC Updates"},
    {"title": "इंग्रजी Grammar मधील Tenses चे सोपे नियम कोणी सांगू शकेल का?", "category": "English"},
    {"title": "नुकत्याच झालेल्या पोलीस भरतीतील कट ऑफ मार्क्स विषयी माहिती कुणाकडे आहे का?", "category": "पोलीस भरती"}
]

BOT_USERS = [
    {"user_id": "bot_01", "user_name": "सचिन पाटील"},
    {"user_id": "bot_02", "user_name": "स्नेहल जगताप"},
    {"user_id": "bot_03", "user_name": "राहुल शिंदे"},
    {"user_id": "bot_04", "user_name": "पूजा देशमुख"},
    {"user_id": "bot_05", "user_name": "अमित पवार"}
]

def post_to_supabase(question_data, user_data):
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # तुमच्या ॲपमधील 'posts' टेबलनुसार योग्य कॉलम नावे (तुमच्या ॲपच्या स्ट्रक्चरनुसार title/content 
        # किंवा category ची नावे खालीलप्रमाणे आहेत, ती एकदा तपासून घ्या)
        payload = {
            "user_id": user_data["user_id"],
            "user_name": user_data["user_name"],
            "title": question_data["title"],
            "category": question_data["category"],
            "upvotes": 0,
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }
        
        # इथे 'forum_posts' ऐवजी आता अचूक 'posts' टेबल वापरले आहे
        response = supabase.table("posts").insert(payload).execute()
        print(f"Successfully posted to Supabase 'posts' table: '{question_data['title']}' by {user_data['user_name']}")
    except Exception as e:
        print(f"Error inserting to Supabase: {e}")
        raise e

def main():
    if not is_within_active_hours():
        print("Outside active hours (7 AM - 10 PM IST). Skipping execution.")
        return

    print("Active Hours Started! Posting 2 random questions...")
    
    for i in range(2):
        delay_seconds = random.randint(10, 60) # टेस्टसाठी वेळ कमी ठेवलाय, हवा तर वाढवू शकता
        print(f"Waiting {delay_seconds} seconds before Question {i+1}...")
        time.sleep(delay_seconds)
        
        q = random.choice(QUESTION_POOL)
        u = random.choice(BOT_USERS)
        
        post_to_supabase(q, u)

if __name__ == "__main__":
    main()

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

# स्पर्धा परीक्षांचे दर्जेदार प्रश्न आणि माहितीपूर्ण कंटेंट
QUESTION_POOL = [
    {
        "title": "MPSC Combined पूर्व परीक्षेसाठी चालू घडामोडीचे किती महिन्यांचे रीडिंग पुरेसे आहे?", 
        "content": "नमस्कार मित्रांनो, आगामी MPSC Combined परीक्षेसाठी चालू घडामोडींचा अभ्यास करताना मागील किमान १ वर्ष की दीड वर्षाचा डेटा वाचायला हवा? कृपया अनुभवी विद्यार्थ्यांनी मार्गदर्शन करावे.",
        "category": "MPSC"
    },
    {
        "title": "महाराष्ट्रातील सर्वात लांब नदी कोणती आणि तिची लांबी किती आहे?", 
        "content": "गोदावरी नदी महाराष्ट्रातील सर्वात लांब नदी आहे, महाराष्ट्रात तिची लांबी किती किलोमीटर आहे याबद्दल कन्फ्युजन आहे. योग्य माहिती सांगा.",
        "category": "भूगोल"
    },
    {
        "title": "मराठी व्याकरणातील 'प्रयोग' या घटकावर सोप्या ट्रिक्स किंवा नोट्स मिळतील का?", 
        "content": "कर्तरी, कर्मणी आणि भावे प्रयोग ओळखताना बऱ्याचदा गोंधळ होतो. कुणाकडे यावर काही शॉर्टकट ट्रिक्स किंवा नोट्स असतील तर इथे शेअर करा.",
        "category": "मराठी"
    },
    {
        "title": "अहिल्यानगर (अहमदनगर) जिल्ह्याचे नवीन नामांतर अधिकृतपणे कधी लागू झाले?", 
        "content": "अहिल्यानगर नामांतराबाबत शासकीय राजपत्र किंवा अधिकृत तारीख काय आहे? स्पर्धा परीक्षेत यावर प्रश्न येऊ शकतो.",
        "category": "सामान्य ज्ञान"
    },
    {
        "title": "तलाठी आणि सरळसेवा भरतीसाठी गणिताच्या सरावासाठी कोणते पुस्तक सर्वोत्तम आहे?", 
        "content": "पंढरपूरकर सर की आर.एस. अग्रवाल? बेसिक पासून तयारी करण्यासाठी कोणते बुक बेस्टराहील सुचवा.",
        "category": "गणिते & बुद्धिमत्ता"
    },
    {
        "title": "भारतीय राज्यघटनेतील कलम ३७० बाबत महत्त्वाचे कायदेशीर मुद्दे कोणते?", 
        "content": "कलम ३७० रद्द करण्याबाबत नुकत्याच झालेल्या सर्वोच्च न्यायालयाच्या निकालावर अभ्यास करताना कोणते पॉईंट्स लक्षात ठेवले पाहिजेत?",
        "category": "राज्यशास्त्र"
    },
    {
        "title": "MPSC राज्यसेवा मुख्य परीक्षेचा नवीन वर्णनात्मक (Descriptive) पॅटर्न कसा आहे?", 
        "content": "नवीन पॅटर्ननुसार उत्तर कसे लिहावे आणि मराठी-इंग्रजी भाषेचे स्वरूप कसे असेल, याबद्दल मार्गदर्शन हवे आहे.",
        "category": "MPSC Updates"
    }
]

# बॉट युझर्स (नाव, आयडी, बॅज आणि अचूक ॲवतार मॅचिंग)
BOT_USERS = [
    {"user_id": "bot_01", "user_name": "सचिन पाटील", "badge": "Gold Member", "avatar": "adhikari-avatar-male-3"},
    {"user_id": "bot_02", "user_name": "स्नेहल जगताप", "badge": "Topper", "avatar": "adhikari-avatar-female-8"},
    {"user_id": "bot_03", "user_name": "राहुल शिंदे", "badge": "Contributor", "avatar": "adhikari-avatar-male-3"},
    {"user_id": "bot_04", "user_name": "पूजा देशमुख", "badge": "Active Learner", "avatar": "adhikari-avatar-female-8"},
    {"user_id": "bot_05", "user_name": "अमित पवार", "badge": "Moderator", "avatar": "adhikari-avatar-male-3"}
]

def post_to_supabase(question_data, user_data):
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # तुमच्या Supabase टेबलच्या हुबेहूब कॉलम नावानुसार Payload
        payload = {
            "author_id": user_data["user_id"],
            "author_name": user_data["user_name"],
            "author_badge": user_data["badge"],
            "author_avatar_url": user_data["avatar"],
            "title": question_data["title"],
            "content": question_data["content"],
            "category": question_data["category"],
            "report_count": 0,
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }
        
        response = supabase.table("posts").insert(payload).execute()
        print(f"Successfully posted to Supabase 'posts': '{question_data['title']}' by {user_data['user_name']}")
    except Exception as e:
        print(f"Error inserting to Supabase: {e}")
        raise e

def main():
    if not is_within_active_hours():
        print("Outside active hours (7 AM - 10 PM IST). Skipping execution.")
        return

    print("Active Hours Started! Posting 2 random questions...")
    
    for i in range(2):
        delay_seconds = random.randint(5, 30)
        print(f"Waiting {delay_seconds} seconds before Question {i+1}...")
        time.sleep(delay_seconds)
        
        q = random.choice(QUESTION_POOL)
        u = random.choice(BOT_USERS)
        
        post_to_supabase(q, u)

if __name__ == "__main__":
    main()

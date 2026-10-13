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
    // --- 1. PLAIN MARATHI (शुद्ध मराठी) ---
    {
        "title": "MPSC राज्यसेवा पूर्व परीक्षेसाठी सीसॅट (CSAT) विषयाची तयारी कशी करावी?",
        "content": "मित्रानो, CSAT हा विषय आता अर्हताकारी (Qualifying) झाला आहे. तरीसुद्धा यामध्ये पासिंग मार्क्स मिळवण्यासाठी उतारे (Comprehension) आणि रीझनिंगचा सराव कसा करावा? मार्गदर्शन करा.",
        "category": "MPSC"
    },
    {
        "title": "महाराष्ट्रातील अष्टविनायकांपैकी पुण्यामध्ये किती मंदिरे आहेत?",
        "content": "अष्टविनायक यात्रा करताना पुणे जिल्ह्यात किती गणपतीची मंदिरे येतात? त्यांची नावे आणि गावे सांगू शकाल का?",
        "category": "भूगोल"
    },
    {
        "title": "महाराष्ट्र पोलीस भरती २०२६ साठी वयोमर्यादा आणि शारीरिक चाचणीचे गुण किती असतात?",
        "content": "पोलीस शिपाई पदासाठी मैदानी चाचणी (Physical Test) ५० गुणांची की १०० गुणांची असते? आणि लेखी परीक्षेचे स्वरूप कसे असते?",
        "category": "पोलीस भरती"
    },
    {
        "title": "मराठी व्याकरणातील 'समास' ओळखण्यासाठी काही सोप्या युक्त्या सांगू शकाल का?",
        "content": "द्वंद्व, अव्ययीभाव आणि बहुव्रीही समास ओळखताना परीक्षा केंद्रावर खूप गोंधळ होतो. यासाठी काही सोप्या ट्रिक्स किंवा शॉर्ट नोट्स असतील तर शेअर करा.",
        "category": "मराठी"
    },
    {
        "title": "१८५७ च्या उठवात महाराष्ट्रातून कोणी मुख्य नेतृत्व केले होते?",
        "content": "आद्यक्रांतीकारक उमाजी नाईक, वासुदेव बळवंत फडके आणि उमाजी नाईक यांच्या योगदानावर प्रश्न विचारले जातात. १८५७ च्या संदर्भात महाराष्ट्रातील मुख्य केंद्र कोणती होती?",
        "category": "इतिहास"
    },
    {
        "title": "आरोग्य विभाग भरतीसाठी तांत्रिक (Technical) प्रश्नांची तयारी कशी करावी?",
        "content": "औषध निर्माण अधिकारी (Pharmacist) आणि परिचारिका (Nurse) पदांसाठी तांत्रिक विषयावर कोणते संदर्भ पुस्तक वापरावे?",
        "category": "सरळसेवा भरती"
    },
    {
        "title": "भारताच्या सर्वोच्च न्यायालयाच्या न्यायाधीशांची नियुक्ती कोण करते?",
        "content": "कोलिजिअम पद्धत म्हणजे काय आणि राष्ट्रपतींची भूमिका काय असते? राज्यशास्त्र अभ्यासासाठी सोप्या भाषेत सांगा.",
        "category": "राज्यशास्त्र"
    },
    {
        "title": "बुद्धिमत्ता चाचणीतील 'नातेसंबंध' (Blood Relations) प्रश्नांसाठी शॉर्टकट ट्रिक्स हव्या आहेत.",
        "content": "वेळ वाचवण्यासाठी डायग्राम पद्धतीने नातेसंबंध कसे सोडवावेत? काही उदाहरणांसह स्पष्ट करा.",
        "category": "गणिते & बुद्धिमत्ता"
    },
    {
        "title": "महाराष्ट्रात सर्वाधिक सिंचन क्षेत्र असलेला जिल्हा कोणता?",
        "content": "कृषी भूगोल अभ्यासत असताना विहीर सिंचन आणि कालवा सिंचनामध्ये कोणते जिल्हे आघाडीवर आहेत?",
        "category": "भूगोल"
    },
    {
        "title": "नुकत्याच झालेल्या क्रीडा स्पर्धांमध्ये भारताला सुवर्णपदक मिळवून देणारे खेळाडू कोण?",
        "content": "चालू घडामोडींसाठी ऑलंपिक, एशियन गेम्स आणि राष्ट्रीय खेळांमधील महाराष्ट्राच्या पदकविजेत्या खेळाडूंची यादी हवी आहे.",
        "category": "चालू घडामोडी"
    },

    // --- 2. MARATHI TYPED IN ENGLISH (Manglish / Roman Marathi) ---
    {
        "title": "Talathi Bharti sathi English Grammar chi tayari kashi karaychi?",
        "content": "Maza English thod kalji sarkha ahe. Talathi paper madhe English Grammar sathi konta book sarvat best rahil? Balasaheb Shinde sir ki M.J. Sheikh sir?",
        "category": "English Grammar"
    },
    {
        "title": "MPSC Combined Group B and C prelims chi cut off kiti jau shakte?",
        "content": "Nuktach dileylya MPSC prelims paper cha difficulty level phar jasta hota. Category wise expected cutoff kiti asu shakto? Senior vidyarthyani sangava.",
        "category": "MPSC Updates"
    },
    {
        "title": "Chhatrapati Shivaji Maharajanchi rajdhani Raigad killa kadhi banli?",
        "content": "Shivaji Maharajanchya itihasavar rajyaseveparyant khup prashna yetat. Rajyabhishek aani Raigad fort babat mahatvache mudde sanga.",
        "category": "इतिहास"
    },
    {
        "title": "Arogya Vibhag Bharti chi hall ticket kadhi yenar ahe?",
        "content": "Form bharun khup divas jale ahet, official website var kahi update ahe ka? Kunala kalale asel tar please sanga.",
        "category": "नवीन भरती updates"
    },
    {
        "title": "Ganitatla 'Kesharmal/Percentage' topic sathi soppy tricks ahet ka?",
        "content": "TCS aani IBPS pattern anusar percentage aani profit loss che ganit khup lenghty yetat. Time management kase karaye?",
        "category": "गणिते & बुद्धिमत्ता"
    },
    {
        "title": "Maharashtra Geography sathi K'Sagar ki Deepstambh konta thobad book changle ahe?",
        "content": "Map study sathi konta atlas vaparava? Map varun khup questions yetat combined madhe.",
        "category": "भूगोल"
    },
    {
        "title": "Police Bharti sathi daily ground practice kiti hours karaychi?",
        "content": "Running sathi timing improve hot nahiye. 1600m aani 100m sathi kay diet aani workout schedule follow karava?",
        "category": "पोलीस भरती"
    },
    {
        "title": "Current affairs sathi Parikrama Magazine purese ahe ka?",
        "content": "Monthly magazine vachli tar varshik chalood ghadamodi alag padhaychi garaj ahe ka? Kashi revision karaychi?",
        "category": "चालू घडामोडी"
    },
    {
        "title": "RTI Act 2005 var TCS pattern madhe kase questions vichartat?",
        "content": "Mahiti cha Adhikar adhiniyam var saralseva madhe fix 2-3 questions ahet. Yachi quick revision notes miltee ka?",
        "category": "सामान्य ज्ञान"
    },
    {
        "title": "ZP Bharti Gramsevak padasathi Krushi ghatanavar kay vachava?",
        "content": "Gramsevak sathi technical syllabus madhe krushi shakha related questions ahet. Yachya notes kunakade ahet ka?",
        "category": "सरळसेवा भरती"
    },

    // --- 3. MARATHI AND ENGLISH COMBO (Mixed Language) ---
    {
        "title": "IBPS Pattern नुसार Reasoning चे time management कसे करावे?",
        "content": "Saralseva exam आता IBPS/TCS घेत आहेत. Sitting arrangement आणि Puzzles सोडवताना खूप time जातो. Any daily practice routine or tips?",
        "category": "गणिते & बुद्धिमत्ता"
    },
    {
        "title": "MPSC Mains Descriptive paper साठी Answer Writing Practice कधीपासून स्टार्ट करावी?",
        "content": "Prelims चा syllabus complete झाल्यावर की prelims आधीपासूनच daily 1-2 answers लिहावे? Toppers चे मार्गदर्शन हवे आहे.",
        "category": "MPSC Guidance"
    },
    {
        "title": "Maharashtra Forts आणि त्यांची Geographical location कशी लक्षात ठेवावी?",
        "content": "सह्याद्रीतील किल्ले आणि जिल्हे यांचे matching type questions खूप येतात. Any memory tricks or shortcut Mnemonics to remember easily?",
        "category": "भूगोल"
    },
    {
        "title": "Indian Economy साठी Kolambe sir चे पुस्तक बेस्ट आहे की Ranjan Kolambe sir?",
        "content": "MPSC prelims & mains दोन्हीसाठी Economics clear होण्यासाठी कोणत्या Reference book वर भर दिला पाहिजे?",
        "category": "अर्थशास्त्र"
    },
    {
        "title": "Current Affairs 2026 साठी रोज Newspaper reading गरजेचे आहे का?",
        "content": "Lokmat, Sakal की Loksatta? Which Marathi newspaper is best for MPSC and Saralseva exams prep?",
        "category": "चालू घडामोडी"
    },
    {
        "title": "Science विषय prepared करताना Physics आणि Chemistry वर जास्त focus करावा की Biology वर?",
        "content": "Non-science background विद्यार्थ्यांना General Science ची खूप भीती वाटते. How to score 10+ marks in Science section?",
        "category": "सामान्य विज्ञान"
    },
    {
        "title": "Panchayati Raj system मध्ये 73rd Amendment amendment चे मुख्य points कोणते?",
        "content": "ग्रामपंचायत, पंचायत समिती आणि जिल्हा परिषद यांच्या अधिकारांवर Frequently asked questions ची लिस्ट मिळेल का?",
        "category": "राज्यशास्त्र"
    },
    {
        "title": "Self Study vs Coaching Classes - MPSC Combined साठी काय योग्य ठरेल?",
        "content": "घरून अभ्यास करून Combined Group B clear करता येते का? Dedicated test series लावणे गरजेचे आहे का?",
        "category": "MPSC Guidance"
    },
    {
        "title": "TCS Pattern नुसार English Vocabulary कशी strong करावी?",
        "content": "Synonyms, Antonyms, Idioms and Phrases विचारण्याचे प्रमाण जास्त आहे. Daily किती words पाठ करावेत?",
        "category": "English Grammar"
    },
    {
        "title": "पर्यावरण (Environment) विषयाची MPSC Mains साठी तयारी कशी करावी?",
        "content": "Biodiversity, Global Warming आणि Environmental Acts वर संकल्पनात्मक (Conceptual) प्रश्न कसे विचारले जातात?",
        "category": "पर्यावरण"
    },

    // --- 4. ENGLISH (पूर्ण इंग्रजीत) ---
    {
        "title": "What is the qualification and age limit for MPSC Rajyaseva Exam?",
        "content": "Can final year degree students apply for MPSC Prelims? Please provide details regarding age relaxation for reserved categories.",
        "category": "MPSC Updates"
    },
    {
        "title": "Which are the major rivers forming the drainage system of Maharashtra?",
        "content": "A brief overview of Godavari, Krishna, Bhima, and Tapi river systems is needed for Maharashtra Geography preparation.",
        "category": "भूगोल"
    },
    {
        "title": "How to prepare Indian Polity using M. Laxmikanth for MPSC exams?",
        "content": "Which chapters are most important from M. Laxmikanth's Polity book for Preliminary examination? Need a priority chapter list.",
        "category": "राज्यशास्त्र"
    },
    {
        "title": "What is the difference between TCS and IBPS exam pattern for Maharashtra exams?",
        "content": "Many Saralseva exams are conducted by TCS/IBPS. How do their math and reasoning questions differ in difficulty level?",
        "category": "Exam Strategy"
    },
    {
        "title": "Important Constitutional Amendments related to Maharashtra State.",
        "content": "List of key constitutional amendments that are frequently asked in MPSC and other competitive exams with brief notes.",
        "category": "राज्यशास्त्र"
    },
    {
        "title": "Best strategy to cover Ancient and Medieval History for State Service Exam.",
        "content": "Since marks weightage for Ancient & Medieval History has increased, which NCERTs or State Board books should I read?",
        "category": "इतिहास"
    },
    {
        "title": "Key highlights of the latest Union Budget and Economic Survey of Maharashtra.",
        "content": "Where can I get concise summary notes for Maharashtra Economic Survey specifically tailored for MPSC aspirants?",
        "category": "अर्थशास्त्र"
    },
    {
        "title": "How to solve Quantitative Aptitude Speed Math for Banking and Saralseva exams?",
        "content": "Tips to improve calculation speed for Simplification, Approximation, and Data Interpretation (DI) problems.",
        "category": "गणिते & बुद्धिमत्ता"
    },
    {
        "title": "What are the major Soil Types found in Maharashtra and their distribution?",
        "content": "Details about Black Cotton Soil (Regur), Laterite Soil, and Alluvial Soil in Maharashtra for Geography section.",
        "category": "भूगोल"
    },
    {
        "title": "Role of Social Reformers of Maharashtra in Modern Indian History.",
        "content": "Notes on Mahatma Phule, Savitribai Phule, Chhatrapati Shahu Maharaj, and Dr. B.R. Ambedkar for exam point of view.",
        "category": "इतिहास"
    },

    // --- 5. MIXED REPEATED VARIATIONS (अजून विविध प्रश्न) ---
    {
        "title": "मराठी भाषा गौरव दिन कधी साजरा केला जातो आणि तो कोणाच्या स्मरणार्थ असतो?",
        "content": "कुसुमाग्रज (वि. वा. शिरवाडकर) यांच्या जयंतीनिमित्त हा दिवस साजरा होतो. या संदर्भातील साहित्य पुरस्कारांवर प्रश्न येतात का?",
        "category": "सामान्य ज्ञान"
    },
    {
        "title": "Police Bharti physical exam madhe chest / height measurement che rules kay ahet?",
        "content": "Male and female candidates sathi mandatory physical standards kay ahet? Reservation wise relaxation milte ka?",
        "category": "पोलीस भरती"
    },
    {
        "title": "MPSC STI, ASO, आणि PSI पदांसाठी Physical and Educational Eligibility काय आहे?",
        "content": "Sub-Inspector (PSI) साठी physical standard काय लागतात? Height, Chest measurements आणि Physical test चे marks कसे काउंट होतात?",
        "category": "MPSC Guidance"
    },
    {
        "title": "What are the major UNESCO World Heritage Sites in Maharashtra?",
        "content": "Information regarding Ajanta Caves, Ellora Caves, Elephanta Caves, Chhatrapati Shivaji Maharaj Terminus, and Western Ghats.",
        "category": "सामान्य ज्ञान"
    },
    {
        "title": "महाराष्ट्रातील मुख्य प्रशासकीय विभाग (Administrative Divisions) किती आणि कोणते?",
        "content": "छत्रपती संभाजीनगर, पुणे, कोकण, नाशिक, नागपूर, अमरावती या विभागात येणाऱ्या जिल्ह्यांची यादी सोप्या पद्धतीने कशी लक्षात ठेवावी?",
        "category": "भूगोल"
    },
    {
        "title": "Zilla Parishad Aarogya Sevak syllabus and exam date update?",
        "content": "Aarogya Sevak male/female post sathi technical subject che 40 questions rahnar ahet. Yachi tayari kashi karaychi?",
        "category": "सरळसेवा भरती"
    },
    {
        "title": "Reasoning मध्ये Syllogism (तर्क व अनुमान) चक्का ५ सेकंदात कसा सोडावा?",
        "content": "Venn Diagram method वापरावी की 100-50 formula? Which approach is fast and 100% accurate for TCS exams?",
        "category": "गणिते & बुद्धिमत्ता"
    },
    {
        "title": "महाराष्ट्रातील संत साहित्य आणि वारकरी संप्रदाय यावर स्पर्धा परीक्षेत येणारे प्रश्न.",
        "content": "संत ज्ञानेश्वर, संत तुकाराम, संत एकनाथ यांच्या रचना, ग्रंथ आणि गाथा यावर वारंवार विचारल्या जाणाऱ्या प्रश्नांची यादी.",
        "category": "इतिहास"
    },
    {
        "title": "How to revise entire syllabus in the last 30 days before exam?",
        "content": "Suggest a daily study schedule, mock test frequency, and revision strategy for final 1 month before MPSC Prelims.",
        "category": "Exam Strategy"
    },
    {
        "title": "MPSC Prelims Answer Key आणि Objection Form कसा सबमिट करायचा?",
        "content": "First answer key आल्यावर चुकीच्या प्रश्नांवर Objections घेण्याची पद्धत काय असते? किती फी असते?",
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

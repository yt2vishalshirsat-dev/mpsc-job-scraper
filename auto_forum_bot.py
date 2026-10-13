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
    },
    {
        "title": "MPSC द्वारे होणाऱ्या तलाठी (ग्राम महसूल अधिकारी) भरतीचे नवीन परीक्षेचे स्वरूप कसे आहे?",
        "content": "शासनाने तलाठी भरती MPSC कडे वर्ग केल्यावर आता परीक्षा दोन टप्प्यात (पूर्व आणि मुख्य) होणार की थेट एकाच टप्प्यात? OMR आधारित परीक्षेचे स्वरूप स्पष्ट करा.",
        "category": "MPSC Talathi"
    },
    {
        "title": "MPSC गट-क संयुक्त पूर्व परीक्षेत तलाठी पदासाठी कट-ऑफ कसा निश्चित होतो?",
        "content": "गट-क पूर्व परीक्षा ही सर्व पदांसाठी एकच असते की तलाठी (Gram Mahsul Adhikari) पदासाठी स्वतंत्र कट-ऑफ जाहीर केला जातो? सविस्तर माहिती हवी आहे.",
        "category": "MPSC Talathi"
    },
    {
        "title": "MPSC तलाठी परीक्षेसाठी शैक्षणिक पात्रता आणि एमएससीआयटी (MS-CIT) बाबत काय नियम आहेत?",
        "content": "कोणत्याही शाखेतील पदवीधर या परीक्षेसाठी पात्र आहेत का? तसेच अर्ज करताना MS-CIT किंवा संगणक अर्हता प्रमाणपत्र लगेच लागते की नियुक्तीनंतर सादर करता येते?",
        "category": "MPSC Talathi"
    },
    {
        "title": "महाराष्ट्र महसूल अधिनियम आणि जमीन सुधारणा कायद्यांचा अभ्यास MPSC तलाठी मुख्य परीक्षेसाठी कसा करावा?",
        "content": "MPSC द्वारे घेतल्या जाणाऱ्या तलाठी मुख्य परीक्षेत महसूल विभागाशी संबंधित विशेष कायदे (उदा. महाराष्ट्र जमीन महसूल संहिता १९६६) विचारले जातात का?",
        "category": "MPSC Talathi"
    },
    {
        "title": "MPSC तलाठी भरती २०२६ साठी नकारात्मक गुणपद्धती (Negative Marking) कशी लागू होते?",
        "content": "पूर्व आणि मुख्य दोन्ही परीक्षांमध्ये १/४ (0.25) निगेटिव्ह मार्किंग असते का? चुकीच्या उत्तरांमुळे गुण कसे कापले जातात ते उदाहरणासह सांगा.",
        "category": "MPSC Talathi"
    },
    {
        "title": "MPSC तलाठी परीक्षेसाठी 'जिल्हा निवड' (District Choice) कशी करावी लागते?",
        "content": "MPSC च्या नवीन नियमांनुसार अर्ज करताना विशिष्ट जिल्ह्यासाठीच अर्ज करावा लागतो की गुणवत्ता यादीनुसार राज्यस्तरावर जिल्हा वाटप होतो?",
        "category": "MPSC Talathi"
    },
    {
        "title": "MPSC तलाठी परीक्षेतील 'अंकगणित आणि बुद्धिमत्ता' घटकाचा काठिण्य पातळीचा स्तर कसा असेल?",
        "content": "पूर्वीच्या TCS/IBPS पॅटर्नपेक्षा MPSC च्या गट-क संयुक्त परीक्षेतील गणितांचे प्रश्न वेगळे असतात का? कोणत्या घटकांवर जास्त भर दिला पाहिजे?",
        "category": "गणिते & बुद्धिमत्ता"
    },
    {
        "title": "MPSC तलाठी पूर्व परीक्षेत सामान्य ज्ञान (GS) विषयातील कोणत्या घटकांना सर्वाधिक वेटेज आहे?",
        "content": "इतिहास, भूगोल, राज्यशास्त्र आणि अर्थव्यवस्था यांपैकी कोणत्या विषयावर जास्त प्रश्न विचारले जातात? पूर्व परीक्षेसाठी मायक्रो-प्लॅनिंग कसे करावे?",
        "category": "सामान्य ज्ञान"
    },
    {
        "title": "MPSC गट-क मुख्य परीक्षेतील मराठी व्याकरण आणि इंग्रजी विषयाची एकत्रित तयारी कशी करावी?",
        "content": "मुख्य परीक्षेतील पेपर-१ मध्ये भाषेचे १०० प्रश्न असतात. पैकी मराठी आणि इंग्रजी व्याकरण आणि उताऱ्यांवरील प्रश्नांसाठी कोणते सर्वोत्तम संदर्भ ग्रंथ वापरावेत?",
        "category": "MPSC Exam Prep"
    },
    {
        "title": "MPSC तलाठी भरतीसाठी डोमासाईल (अधिवास प्रमाणपत्र) आणि नॉन-क्रिमीलेअर (NCL) ची वैधता तारीख कोणती असावी?",
        "content": "फॉर्म भरण्याच्या अंतिम तारखेपूर्वीचे प्रमाणपत्र असावे लागते का? प्रमाणपत्र अपलोड करताना कोणत्या तांत्रिक गोष्टींची काळजी घ्यावी?",
        "category": "MPSC Talathi"
    },

    // ==========================================
    // 2. MARATHI TYPED IN ENGLISH (Manglish / Roman)
    // ==========================================
    {
        "title": "MPSC Talathi Bharti sathi Group C Combined Prelims chi cutoff kiti jau shakte?",
        "content": "MPSC kadun Conduct honarya Talathi (Gram Mahsul Adhikari) sathi 100 marks paiki safe score kiti raheel? General aani Reserved category sathi kay target thevava?",
        "category": "MPSC Talathi"
    },
    {
        "title": "MPSC Talathi exam sathi OMR Sheet bharatana konte rules lakshat thevave?",
        "content": "Offline exam honar ahe tar Black ball pen vaparava ki Blue? Double circle kelyas negative marking lagte ka? Exam center var konti kaalji ghyavi?",
        "category": "Exam Strategy"
    },
    {
        "title": "Purvi TCS ghenyat yenari Talathi Bharti aani ata MPSC Talathi madhe kay farak ahe?",
        "content": "Question paper format, negative marking aani difficulty level madhe kay badal jala ahe? Senior aspirants ni MPSC pattern nusar tips dhyavat.",
        "category": "MPSC Talathi"
    },
    {
        "title": "MPSC Talathi Bharti sathi Typing Certificate compuslory ahe ka?",
        "content": "Gram Mahsul Adhikari (Talathi) post sathi English 40 WPM ki Marathi 30 WPM typing lagte ka? Form bharta veli typing detail lagtat ka?",
        "category": "MPSC Talathi"
    },
    {
        "title": "Talathi Mains exam sathi Geography & History of Maharashtra cha depth kiti asava?",
        "content": "MPSC pattern nusar Maharashtra chya Bhugolavar aani Samajshastradnyanvar jatast questions yetat ka? Kontya standard books vachava?",
        "category": "भूगोल & इतिहास"
    },
    {
        "title": "MPSC Talathi Hall Ticket aani Exam Center change babat kay update ahe?",
        "content": "MPSC profile madhun preferred exam centre select karta yete ka? Admit card exam chya kiti divas aadhi mpsconline portal var upload hote?",
        "category": "MPSC Updates"
    },
    {
        "title": "MPSC Group C Prelims madhe Science subject sathi 10+ marks kase score karaye?",
        "content": "Physics, Chemistry aani Biology packet MPSC Talathi pre exam sathi State Board 8th-10th books purese ahet ka ki Lucent GS vachava?",
        "category": "सामान्य विज्ञान"
    },
    {
        "title": "Talathi Bharti age limit calculation date konti dharli jate?",
        "content": "MPSC notification nusar Open category sathi 38 years aani Reserved category sathi 43 years age limit gannasathi cut-off date kashi thartat?",
        "category": "MPSC Talathi"
    },
    {
        "title": "MPSC Talathi exam sathi Current Affairs kiti mahine aadhiche vachave?",
        "content": "Exam date chya aadhi 1 year cha Current Affairs vachawa ki 1.5 years cha? Maharashtra Specific Schemes aani Land Revenue updates var questions yetat ka?",
        "category": "चालू घडामोडी"
    },
    {
        "title": "MPSC Talathi posts sathi Salary structure aani Pay Scale kay ahe?",
        "content": "7th Pay Commission Level S-8 nusar Talathi (Gram Mahsul Adhikari) cha starting In-hand salary, DA, HRA aani allowances kiti miltat?",
        "category": "MPSC Talathi"
    },

    // ==========================================
    // 3. MARATHI & ENGLISH COMBO (Mixed Language)
    // ==========================================
    {
        "title": "MPSC Talathi Exam Pattern: Preliminary vs Mains Examination मध्ये काय फरक आहे?",
        "content": "Prelims फक्त Qualifying स्वरूपाची आहे का? आणि Final Selection मेरिट लिस्ट फक्त Mains परीक्षांच्या गुणांवर बनते का? Detailed stage-wise selection process सांगा.",
        "category": "MPSC Talathi"
    },
    {
        "title": "MPSC Group C Prelims मधील English Language आणि Grammar ची तयारी कशी करावी?",
        "content": "MPSC pattern नुसार Passage Reading, Vocabulary आणि Grammar Structure वर कसा फोकस ठेवावा? M.J. Sheikh किंवा Balasaheb Shinde सर यांचे पुस्तक पुरेसे आहे का?",
        "category": "English Grammar"
    },
    {
        "title": "MPSC Talathi post साठी District-wise Vacancies आणि Post Allocation कसे होते?",
        "content": "महाराष्ट्र लोकसेवा आयोगाद्वारे (MPSC) सर्व जिल्ह्यांसाठी एकच Merit List जाहीर होणार की Candidate ने निवडलेल्या जिल्ह्यानुसार Merit ठरणार?",
        "category": "MPSC Talathi"
    },
    {
        "title": "Polity (राज्यशास्त्र) मधील 'महसूल प्रशासन' (Revenue Administration) चा अभ्यास MPSC साठी कसा करावा?",
        "content": "जिल्हाधिकारी, उपविभागीय अधिकारी (SDO), तहसीलदार आणि तलाठी यांचे अधिकार व कर्तव्य यावर MPSC मध्ये कसे Multiple Choice Questions (MCQs) येतात?",
        "category": "राज्यशास्त्र"
    },
    {
        "title": "MPSC Talathi Prelims OMR-based test वेळेत पूर्ण करण्यासाठी Speed and Accuracy कशी वाढवावी?",
        "content": "१ तासात १०० प्रश्न (100 Questions in 60 Minutes) सोडवणे आव्हानात्मक असते. Time Management आणि Mock Test Analysis कसा करावा?",
        "category": "Exam Strategy"
    },
    {
        "title": "MPSC Talathi recruitment साठी EWS आणि Non-Creamy Layer (NCL) संदर्भातील नियमावली काय आहे?",
        "content": "Financial year 2025-26 चे EWS certificate चालेल का? Application Form सबमिट करताना लागणारे Certificate validity चे क्रायटेरिया सांगा.",
        "category": "MPSC Rules"
    },
    {
        "title": "MPSC Talathi Mains Paper 2 साठी CSAT & Reasoning चा syllabus कसा कवर करावा?",
        "content": "Logic, Data Interpretation, Statement-Assumptions आणि Math Tricks साठी दैनिक सराव कसा करावा? MPSC PYQs सोडवणे किती महत्त्वाचे आहे?",
        "category": "गणिते & बुद्धिमत्ता"
    },
    {
        "title": "MPSC Talathi Final Answer Key नंतर MPSC कडे Objections कसे नोंदवावे?",
        "content": "आयोगाने जारी केलेल्या First Key मधील चुकीच्या प्रश्नांवर Proofs (संदर्भ ग्रंथ) सह Objection Raise करण्याची प्रक्रिया आणि Online Portal Fee काय असते?",
        "category": "MPSC Updates"
    },
    {
        "title": "MPSC Talathi exam मधील Negative Marking मुळे न येणारे questions skip करणे योग्य की Risk घेणे?",
        "content": "Elimination Technique वापरून ५०-५० संभ्रम असणारे प्रश्न अटेम्प्ट करावेत का? Accuracy राखण्यासाठी Toppers चा काय सल्ला असतो?",
        "category": "Exam Strategy"
    },
    {
        "title": "MPSC Talathi post भरतीसाठी Document Verification (DV) मध्ये कोणती कागदपत्रे लागतात?",
        "content": "Caste Certificate, Validity, Domicile, SSC Board Certificate, Degree Marksheet आणि Small Family Declaration Form याबद्दल सविस्तर चेकलिस्ट हवी आहे.",
        "category": "MPSC Guidelines"
    },

    // ==========================================
    // 4. ENGLISH (पूर्ण इंग्रजीत)
    // ==========================================
    {
        "title": "What is the complete selection process for Talathi (Gram Mahsul Adhikari) via MPSC?",
        "content": "Detailed overview of Maharashtra Group-C Services Combined Preliminary Examination and the dedicated Main Examination conducted by MPSC for Revenue Officer posts.",
        "category": "MPSC Talathi"
    },
    {
        "title": "What is the detailed syllabus for MPSC Group C Combined Preliminary Exam for Talathi post?",
        "content": "Subject-wise weightage for History, Geography, Polity, Economics, General Science, Current Affairs, and Mental Ability in the 100-mark Preliminary Test.",
        "category": "MPSC Syllabus"
    },
    {
        "title": "Is a Domicile Certificate compulsory for applying to the MPSC Talathi Recruitment?",
        "content": "What are the essential Maharashtra Domicile rules and relaxed criteria for candidates residing in border areas like Maharashtra-Karnataka border?",
        "category": "MPSC Eligibility"
    },
    {
        "title": "How does MPSC conduct the Offline OMR-based test for Maharashtra Group C posts?",
        "content": "Guidelines on OMR sheet evaluation, carbon copy retention, negative marking calculation, and precautions to avoid answer sheet rejection.",
        "category": "Exam Guidelines"
    },
    {
        "title": "What are the job responsibilities and career growth of a Talathi (Gram Mahsul Adhikari) in Revenue Dept?",
        "content": "Promotion hierarchy from Talathi to Circle Officer (Mandal Adhikari), Naib Tehsildar, and Tehsildar along with duty profile in rural administration.",
        "category": "Career Profile"
    },
    {
        "title": "Which MPSC Previous Year Question Paper (PYQ) books are recommended for Talathi exam?",
        "content": "How many years of MPSC Group C PYQs should be analyzed to understand question trends, repeated concepts, and difficulty level?",
        "category": "Preparation Strategy"
    },
    {
        "title": "What is the marking scheme and time duration for MPSC Group C Mains Examination?",
        "content": "Distribution of marks between Paper 1 (Languages: Marathi & English) and Paper 2 (General Studies & Aptitude Test) for final recruitment.",
        "category": "MPSC Pattern"
    },
    {
        "title": "How to handle Maharashtra Geography and Local Revenue System for MPSC Mains?",
        "content": "Important topics related to Maharashtra agriculture, soil types, river basins, district administration, and land records system (7/12 & 8A extracts).",
        "category": "MPSC Preparation"
    },
    {
        "title": "What is the age relaxation criteria for ex-servicemen, sports persons, and PwD candidates in MPSC Talathi exam?",
        "content": "Maximum age limit relaxations applicable as per Maharashtra Government service reservation norms for various special categories.",
        "category": "MPSC Eligibility"
    },
    {
        "title": "How to effectively manage time between Marathi, English, and Aptitude during MPSC Mains?",
        "content": "Sectional time distribution strategy for clearing high sectional cutoffs in Paper 1 and Paper 2 of MPSC Group-C Main exam.",
        "category": "Exam Strategy"
    },

    // ==========================================
    // 5. ADDITIONAL VARIATIONS (विविधतापूर्ण मिश्र प्रश्न)
    // ==========================================
    {
        "title": "MPSC द्वारे घेण्यात येणाऱ्या तलाठी भरतीत ७/१२ उतारा आणि ८-अ उतारा यावर प्रश्न विचारतात का?",
        "content": "महसूल प्रशासनातील प्राथमिक संकल्पनांचा अभ्यास पूर्व परीक्षेत उपयुक्त ठरतो की मुख्य परीक्षेत? महसूल शब्दावलीची तयारी कशी करावी?",
        "category": "MPSC Talathi"
    },
    {
        "title": "MPSC Talathi form bhartana Maharashtra Domicile uploaded file size aani format kay pahije?",
        "content": "MPSC Portal var Documents upload kartana PDF format required ahe ki JPG? Document size limit (100KB to 500KB) kashi adjust karaychi?",
        "category": "MPSC Portal Help"
    },
    {
        "title": "MPSC Talathi cut-off clearing strategy: १ महिन्यात Revision कशी पूर्ण करावी?",
        "content": "शेवटच्या ३० दिवसांत दररोज किती Mock Tests सोडवाव्यात? MPSC Previous Year Questions (PYQs) ची उजळणी करण्याची योग्य पद्धत कोणती?",
        "category": "Exam Strategy"
    },
    {
        "title": "What is the penalty rule for wrong answers in MPSC OMR-based examinations?",
        "content": "Explanation of 25% or 0.25 negative marks deduction per wrong question and its impact on overall score calculation.",
        "category": "MPSC Rules"
    },
    {
        "title": "MPSC तलाठी परीक्षेसाठी 'इतिहास' घटकात महाराष्ट्रातील समाजसुधारकांवर किती प्रश्न असतात?",
        "content": "महात्मा फुले, डॉ. बाबासाहेब आंबेडकर, छत्रपती शाहू महाराज व महर्षी कर्वे यांच्या कार्यावरील प्रश्नांसाठी कोणते पुस्तक वाचावे?",
        "category": "इतिहास"
    },
    {
        "title": "MPSC Talathi recruitment madhe Parallel Reservation (समांतर आरक्षण) kase lagu hote?",
        "content": "Women reservation, Sports persons, Orphan (अनाथ), aani Ex-servicemen sathi parallel reservation MPSC kase apply karte?",
        "category": "MPSC Rules"
    },
    {
        "title": "MPSC गट-क परीक्षा केंद्रावर सोबत कोणती ओळखपत्रे (ID Proofs) नेणे बंधनकारक आहे?",
        "content": "आधार कार्ड, पॅन कार्ड किंवा ड्रायव्हिंग लायसन्सची मूळ प्रत आणि झेरॉक्स प्रत सोबत नेण्याबाबत MPSC च्या अधिकृत सूचना काय आहेत?",
        "category": "Exam Guidelines"
    },
    {
        "title": "How to prepare Current Affairs specific to Maharashtra Schemes for MPSC Talathi exam?",
        "content": "Key government welfare schemes, agricultural policies, and administrative infrastructure developments in Maharashtra to focus on.",
        "category": "चालू घडामोडी"
    },
    {
        "title": "MPSC तलाठी पूर्व परीक्षेत Pass झाल्यावर Mains Exam साठी पुन्हा वेगळा Form भरावा लागतो का?",
        "content": "मुख्य परीक्षेसाठी पुन्हा फी भरावी लागते का आणि केंद्र निवडीचा पर्याय पुन्हा उपलब्ध होतो का?",
        "category": "MPSC Updates"
    },
    {
        "title": "MPSC Talathi Bharti Mains Paper-1 Marathi Vyakaran sathi K'Sagar ki Balasaheb Shinde?",
        "content": "समानार्थी शब्द, विरुद्धार्थी शब्द, म्हणी व वाक्प्रचार यांचा सराव करण्यासाठी रोज किती वेळ द्यावा?",
        "category": "मराठी व्याकरण"
    },
    {
        "title": "महाराष्ट्र पोलीस भरतीसाठी शारीरिक पात्रता (Height & Chest) आणि वयोमर्यादा काय आहे?",
        "content": "पोलीस शिपाई पदासाठी खुला (Open) आणि मागासवर्गीय प्रवर्गातील मुला-मुलींसाठी किमान व कमाल वयोमर्यादा आणि उंची-छातीची मोजमापे काय लागतात?",
        "category": "पोलीस भरती"
    },
    {
        "title": "पोलीस भरती मैदानी चाचणी (Physical Test) ५० गुणांची कशी विभाजित केलेली असते?",
        "content": "पुरुष उमेदवारांसाठी १६०० मीटर धावणे, १०० मीटर धावणे आणि गोळाफेक यासाठी गुणांचे वितरण कसे असते? सविस्तर तक्ता सांगा.",
        "category": "पोलीस भरती"
    },
    {
        "title": "पोलीस भरतीत आधी मैदानी चाचणी (Physical) होते की लेखी परीक्षा (Written Exam)?",
        "content": "नवीन पोलीस भरती नियमांनुसार मैदानी चाचणीत किमान किती टक्के गुण मिळवणारे उमेदवार लेखी परीक्षेसाठी पात्र ठरतात?",
        "category": "पोलीस भरती"
    },
    {
        "title": "पोलीस शिपाई लेखी परीक्षेत एकूण किती प्रश्न असतात आणि वेळ किती मिळतो?",
        "content": "१०० गुणांच्या OMR आधारित लेखी परीक्षेत मराठी व्याकरण, गणित, बुद्धिमत्ता आणि सामान्य ज्ञान या विषयांना प्रत्येकी किती गुण असतात?",
        "category": "पोलीस भरती"
    },
    {
        "title": "पोलीस भरती चालक (Driver) पदासाठी हलके/जड वाहन चालक परवाना (Driving License) कधी लागते?",
        "content": "चालक पदासाठी RTO ड्रायव्हिंग टेस्ट ५० गुणांची स्वतंत्रपणे घेतली जाते का? यामध्ये Skill Test कशी होते?",
        "category": "पोलीस चालक"
    },
    {
        "title": "राज्य राखीव पोलीस बल (SRPF) भरतीसाठी पुरुष उमेदवारांची मैदानी चाचणी किती गुणांची असते?",
        "content": "SRPF मध्ये ५ किमी धावणे (5 KM Running) असते का? SRPF आणि जिल्हा पोलीस शिपाई यांच्या फिजिकल टेस्टमध्ये काय फरक आहे?",
        "category": "SRPF भरती"
    },
    {
        "title": "पोलीस भरती लेखी परीक्षेत 'नकारात्मक गुणपद्धती' (Negative Marking) लागू असते का?",
        "content": "गलत उत्तरांसाठी गुण कापले जातात का? OMR सीट भरताना कोणती काळजी घ्यावी जेणेकरून गुण वजा होणार नाहीत?",
        "category": "पोलीस भरती"
    },
    {
        "title": "महाराष्ट्रातील पोलीस प्रशासन, परिक्षेत्र आणि आयुक्तालय यावर कसे प्रश्न विचारले जातात?",
        "content": "महाराष्ट्रात एकूण किती पोलीस आयुक्तालय (Commissionerates) आणि पोलीस परिक्षेत्र (Ranges) आहेत? DG Office संदर्भातील चालू घडामोडी कशा अभ्यासाव्यात?",
        "category": "सामान्य ज्ञान"
    },
    {
        "title": "पोलीस भरती मराठी व्याकरणासाठी बाळासाहेब शिंदे की मो. रा. वाळंबे कोणते पुस्तक वापरावे?",
        "content": "मराठी व्याकरणातील २५ गुणांपैकी २५ गुण मिळवण्यासाठी प्रयोग, समास, अलंकार आणि वाक्प्रचारांची तयारी कशी करावी?",
        "category": "मराठी व्याकरण"
    },
    {
        "title": "पोलीस भरती अंतिम निवड यादी (Final Merit List) कशी तयार केली जाते?",
        "content": "मैदानी चाचणीचे ५० गुण आणि लेखी परीक्षेचे १०० गुण मिळून १५० पैकी मेरिट ठरते का? कट-ऑफ कसा निश्चित होतो?",
        "category": "पोलीस भरती"
    },

    // ==========================================
    // 2. MARATHI TYPED IN ENGLISH (Manglish / Roman)
    // ==========================================
    {
        "title": "Police Bharti 1600 Meter running timing kashi kamii karaychi?",
        "content": "1600m run 5 minute 10 second chya aath complete karaychi ahe. Weekly stamina build aani interval running schedule kay asava?",
        "category": "Physical Fitness"
    },
    {
        "title": "Police Bharti sathi Gola Phek (Shot Put) madhe out-of marks kase ghyaye?",
        "content": "Gola out of (7.260 kg) feknayasathi shoulder strength aani throwing technique kashi improve karaychi? Any exercise tips?",
        "category": "Physical Fitness"
    },
    {
        "title": "Police Bharti Document Verification (DV) madhe konte certificates mandatory ahet?",
        "content": "Form bharta veli 10th-12th marksheets, Domicile, Non-Creamy Layer (NCL), Caste Certificate aani Aadhaar card var naavat badal aslyas kay karaye?",
        "category": "Police Bharti"
    },
    {
        "title": "Police Bharti Written Exam madhe Math aani Reasoning sathi fast calculation tricks?",
        "content": "100 marks paiki Math & Reasoning che 50 marks ahet. Time management kase karaye aani Pandharinath Rane sir chya pustakatun kay abhyasava?",
        "category": "गणिते & बुद्धिमत्ता"
    },
    {
        "title": "Women candidate sathi Police Bharti Physical Test che marks distribution kase aste?",
        "content": "Female aspirants sathi 800m running, 100m running aani Shot Put (4kg) sathi kiti marks ahet? Out-of marks milvanya sathi target timing kay paije?",
        "category": "Police Bharti"
    },
    {
        "title": "Police Bharti ekach veli don jillhyat (Districts) form bharu shakto ka?",
        "content": "Dual form bharla tar candidate reject hoto ka? Government rules aani official notification madhe kay spashtikaran ahe?",
        "category": "Police Bharti Rules"
    },
    {
        "title": "Police Bharti Hall Ticket aani Physical Exam date kashi check karaychi?",
        "content": "Mahapolice official portal var admit card aalya var ground center aani batch timing kashi samajte? Physical test varsha-rutut hote ka?",
        "category": "Police Updates"
    },
    {
        "title": "Police Bharti Current Affairs (चालू घडामोडी) sathi kiti mahine aadhicha data vachava?",
        "content": "Last 6 months ki 1 year? Maharashtra Police Awards, Sports News aani New Appointments var fix questions yetat ka?",
        "category": "चालू घडामोडी"
    },
    {
        "title": "Police Constable Ground Test sathi best Diet Plan aani Stamina Exercise?",
        "content": "Daily morning running nantar shin bone pain aani fatigue kram karnyasathi kay diet ghyava? Protein intake aani recovery timing kashi asavi?",
        "category": "Physical Fitness"
    },
    {
        "title": "Bandssman aani Karagruh Police (Jail Police) Physical Test madhe kay farak ahe?",
        "content": "Jail Police sathi physical cutoff vegla lagto ka? Bandssman post sathi musical instrument test kashi hote?",
        "category": "Police Bharti"
    },

    // ==========================================
    // 3. MARATHI & ENGLISH COMBO (Mixed Language)
    // ==========================================
    {
        "title": "Maharashtra Police Bharti: 100m Sprint मध्ये maximum speed आणि scoring कसे करावे?",
        "content": "100m running चे marks चुकेल न घालवता आउट ऑफ मिळवण्यासाठी Start Block Position, Explosive Power आणि Stride Length वर काम कसे करावे?",
        "category": "Physical Fitness"
    },
    {
        "title": "Police Bharti GK section मध्ये Maharashtra Police Administration वर किती प्रश्न येतात?",
        "content": "पोलीस महासंचालक (DGP), पोलीस आयुक्त (CP), विशेष पोलीस महानिरीक्षक (IGP) आणि SP रँकची उतरंड (Hierarchy) कशी लक्षात ठेवावी?",
        "category": "सामान्य ज्ञान"
    },
    {
        "title": "Police Bharti Math Syllabus: कोणत्या Chapters वर सर्वाधिक लक्ष दिले पाहिजे?",
        "content": "संख्याशास्त्र, लसावी-मसावी, टक्केवारी, नफा-टोटा, वयोवारी आणि रेल्वे-वेग-वेळ (Speed & Distance) या ५-६ टॉपिक्स वरूनच प्रश्न जास्त येतात का?",
        "category": "गणिते & बुद्धिमत्ता"
    },
    {
        "title": "Police Bharti Ground Test दरम्यान Shin Splints (पायांच्या नडगीचे दुखणे) कसे टाळावे?",
        "content": "Hard road running ऐवजी Mud/Grass track वर सराव करणे, Proper Running Shoes निवडणे आणि Ice Fomentation याविषयी मार्गदर्शन हवे आहे.",
        "category": "Physical Fitness"
    },
    {
        "title": "Police Bharti साठी Home Guard (होमगार्ड) आणि Project Affected (प्रकल्पग्रस्त) Quota चे नियम काय आहेत?",
        "content": "Home guard मधील ३ वर्षे सेवा पूर्ण असलेल्या उमेदवारांना आरक्षण मिळवण्यासाठी कोणते विशेष दाखले आवश्यक असतात?",
        "category": "Police Reservation"
    },
    {
        "title": "Police Bharti Written Test OMR Sheet भरताना ५ कॉमन चुका ज्या टाळल्याच पाहिजेत!",
        "content": "Question paper code चुकीचा भरणे, Roll number बबल्स व्यवस्थित न काळे करणे, किंवा दोन वर्तुळ काळे करणे यामुळे Answer sheet बाद होते का?",
        "category": "Exam Guidelines"
    },
    {
        "title": "Police Constable vs Driver vs SRPF - कोणत्या पोस्टसाठी Apply करणे फायदेशीर ठरेल?",
        "content": "तिन्ही पोस्टचे Work Culture, Promotion Scope आणि Physical Test चा फरक समजून घेऊन Form कसा भरावा?",
        "category": "Police Guidance"
    },
    {
        "title": "Police Bharti Test Series: लेखी परीक्षेच्या १ महिना आधी Weekly किती Mock Tests द्याव्यात?",
        "content": "९० मिनिटांत १०० प्रश्न सोडवण्याची सवय होण्यासाठी ओएमआर सीटवर टाइम लावून पेपर सोडवण्याचा काय फायदा होतो?",
        "category": "Exam Strategy"
    },    {
        "title": "Maharashtra Special Armed Police Act आणि IPC चे बेसिक कायदे लेखी परीक्षेत विचारतात का?",
        "content": "सामान्य पोलीस शिपाई परीक्षेसाठी मोटर वाहन कायदा किंवा मूलभूत पोलीस कायदे अभ्यासावे लागतात की फक्त बेसिक सामान्य ज्ञान पुरेसे आहे?",
        "category": "सामान्य ज्ञान"
    },
    {
        "title": "Police Bharti Medical Examination मध्ये काय काय Check केले जाते?",
        "content": "Eye vision (Color Blindness), Flat Foot, Knock Knee, Tattoo Rules आणि Chest Expansion Test मधील निकष काय असतात?",
        "category": "Medical Test"
    },

    // ==========================================
    // 4. ENGLISH (पूर्ण इंग्रजीत)
    // ==========================================
    {
        "title": "What is the detailed selection criteria for Maharashtra Police Constable Recruitment?",
        "content": "Comprehensive step-by-step evaluation procedure comprising Physical Efficiency Test (PET), OMR Written Examination, Document Verification, and Medical Test.",
        "category": "Police Bharti"
    },
    {
        "title": "What are the physical standards (Height and Chest expansion) for Male and Female candidates?",
        "content": "Minimum height requirement (165 cm for males, 155 cm for females) and chest measurement norms for open and reserved categories in Maharashtra Police.",
        "category": "Eligibility Norms"
    },
    {
        "title": "How to clear the 1600 meters running event within the maximum scoring timing?",
        "content": "Effective track training techniques, breathing control strategies, and pacing methods to complete 1600m in under 5:10 minutes for maximum marks.",
        "category": "Physical Fitness"
    },
    {
        "title": "What is the syllabus and subject-wise mark weightage for Maharashtra Police Written Exam?",
        "content": "Breakdown of 100 marks across Marathi Grammar (25), Mathematics (25), Intelligence Test/Reasoning (25), and General Knowledge & Current Affairs (25).",
        "category": "Exam Syllabus"
    },
    {
        "title": "What are the relaxed physical criteria for Sports Persons and Children of Police Personnel?",
        "content": "Concessions provided in height and chest measurements for certified National/State level sports candidates and police wards.",
        "category": "Police Reservation"
    },
    {
        "title": "What is the driving skill test procedure for Maharashtra Police Driver (Chalak) Recruitment?",
        "content": "Details regarding Light Motor Vehicle (LMV) driving test, Heavy Motor Vehicle test, and traffic rules evaluation conducted for 50 marks.",
        "category": "Police Driver"
    },
    {
        "title": "List of essential documents required during Maharashtra Police Bharti Verification stage.",
        "content": "Checklist including Domicile Certificate, SSC/HSC Passing Certificates, Cast Certificate, Cast Validity, Non-Creamy Layer, and Photo ID proof.",
        "category": "Document Verification"
    },
    {
        "title": "What are the rules regarding Tattoos and Flat Foot in Maharashtra Police Medical Test?",
        "content": "Official medical guidelines on body tattoos, color vision impairment, knock knees, hearing test, and overall physical fitness standards.",
        "category": "Medical Test"
    },
    {
        "title": "How to score 25/25 in Marathi Grammar for Maharashtra Police Recruitment Exam?",
        "content": "Key high-yielding topics such as Samas, Prayog, Vakyaprachar, Mhani, and Sandhi with practice techniques for high accuracy.",
        "category": "मराठी व्याकरण"
    },
    {
        "title": "What is the job role, training duration, and salary scale of a newly appointed Police Constable in Maharashtra?",
        "content": "Details about initial training at Police Training Schools (PTS), monthly basic pay + allowances under the 7th Pay Commission, and duty responsibilities.",
        "category": "Career Profile"
    },

    // ==========================================
    // 5. ADDITIONAL VARIATIONS (विविधतापूर्ण मिश्र प्रश्न)
    // ==========================================
    {
        "title": "महाराष्ट्रातील पोलीस भरतीसाठी अनाथ (Orphan) आरक्षणाचा लाभ कसा घ्यावा?",
        "content": "महिला व बालविकास विभागाचे १% अनाथ प्रमाणपत्र अर्ज करताना जोडणे गरजेचे आहे का? वयोमर्यादा व गुणांमध्ये कोणती सवलत मिळते?",
        "category": "पोलीस नियम"
    },
    {
        "title": "Police Bharti Shot Put feknatana Line Cut (Foul) टाळण्यासाठी काय काळजी घ्यावी?",
        "content": "गोळा टाकल्यानंतरCircle मधून बाहेर पडण्याचा योग्य मार्ग कोणता? ३ संधींमध्ये बेस्ट थ्रो कसा नोंदवला जातो?",
        "category": "Physical Fitness"
    },
    {
        "title": "Police Bharti Written Exam OMR Sheet Pen rules: Gel Pen चालेल की Ball Pen?",
        "content": "0.7mm Black Ball Pen वापरणे का फायदेशीर मानले जाते? Bubble व्यवस्थित fill करण्यासाठी OMR tips सांगा.",
        "category": "Exam Guidelines"
    },
    {
        "title": "How is the cut-off calculated if two candidates score equal marks in Police Bharti?",
        "content": "वयाने मोठा असलेला उमेदवार, शैक्षणिक पात्रता जास्त असलेला, किंवा मैदानी चाचणीत जास्त गुण मिळवलेला candidate यांपैकी कोणाला प्राधान्य दिले जाते?",
        "category": "Police Rules"
    },
    {
        "title": "पोलीस भरती पूर्वतयारी: दररोज मैदानी सराव आणि अभ्यासाचे Time Table कसे असावे?",
        "content": "सकाळी २ तास ग्राउंड, दुपारी ४ तास वाचन आणि संध्याकाळी १ तास गणिताचा सराव असा आदर्श daily routine कसा बनवावा?",
        "category": "Exam Strategy"
    },
    {
        "title": "SRPF Bharti madhe 5 KM running sathi stamina aani speed balance kashi thevavi?",
        "content": "पहिल्या २ किलोमीटर मध्ये धावण्याचा वेग कसा असावा? शेवटच्या ४०० मीटर मध्ये फिनिशिंग स्प्रिंट कशी मारावी?",
        "category": "SRPF भरती"
    },
    {
        "title": "पोलीस भरतीसाठी 'चालू घडामोडी' मधील क्रीडा आणि पुरस्कार घटकाची उजळणी कशी करावी?",
        "content": "अर्जुन पुरस्कार, महाराष्ट्र केसरी, ऑलिम्पिक पदके आणि महाराष्ट्रातील राष्ट्रीय क्रीडा पुरस्कार विजेत्यांची यादी हवी आहे.",
        "category": "चालू घडामोडी"
    },
    {
        "title": "What is the age limit relaxation for Ex-Servicemen (माजी सैनिक) in Maharashtra Police Bharti?",
        "content": "सशस्त्र दलातील सेवा कालावधी + ३ वर्षे अशी वयोमर्यादेतील सवलत कशी लागू होते? शस्त्रास्त्र परवाना किंवा ड्रायव्हिंग लायसन्स आवश्यक आहे का?",
        "category": "Police Rules"
    },
    {
        "title": "पोलीस भरतीत एनसीसी (NCC) 'C' आणि 'B' प्रमाणपत्र धारकांना बोनस गुण कसे मिळतात?",
        "content": "NCC 'C' Certificate असल्यास ५% आणि 'B' Certificate असल्यास ३% अतिरिक्त गुण लेखी परीक्षेत कसे जोडले जातात?",
        "category": "पोलीस नियम"
    },
    {
        "title": "Police Bharti Reasoning Section madhe Coding-Decoding aani Series questions fast kase sodvave?",
        "content": "अक्षरमाला (Alphabets A-Z reverse numbers) आणि वर्ग-घन (Squares & Cubes) तोंडपाठ ठेवल्यास वेळेची बचत कशी होते?",
        "category": "गणिते & बुद्धिमत्ता"
    }
]

# बॉट युझर्स (नाव, आयडी, बॅज आणि अचूक ॲवतार मॅचिंग)
BOT_USERS = [
    {"user_id": "bot_01", "user_name": "सचिन पाटील", "badge": "Gold Member", "avatar": "adhikari-avatar-male-3"},
    {"user_id": "bot_02", "user_name": "स्नेहल जगताप", "badge": "Topper", "avatar": "adhikari-avatar-female-8"},
    {"user_id": "bot_03", "user_name": "राहुल शिंदे", "badge": "Contributor", "avatar": "adhikari-avatar-male-3"},
    {"user_id": "bot_04", "user_name": "पूजा देशमुख", "badge": "Active Learner", "avatar": "adhikari-avatar-female-8"},
    {"user_id": "bot_05", "user_name": "अमित पवार", "badge": "Moderator", "avatar": "adhikari-avatar-male-3"}
    {"user_id": "bot_05", "user_name": "Sagar Shirsat", "badge": "Moderator", "avatar": "adhikari-avatar-male-3"}
    {"user_id": "bot_05", "user_name": "Jalu Bangar", "badge": "Moderator", "avatar": "adhikari-avatar-male-3"}
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

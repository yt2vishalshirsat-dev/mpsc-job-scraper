import sys
import subprocess
import os
import json
import re

# --- FAIL-SAFE AUTO INSTALLER GUARD ---
# जर GitHub एनव्हायरनमेंटमध्ये लायब्ररी मिसिंग असेल तर रनटाईमला स्वतः इन्स्टॉल करेल
required_packages = [
    ('requests', 'requests'),
    ('bs4', 'beautifulsoup4'),
    ('firebase_admin', 'firebase-admin')
]

for mod, pkg in required_packages:
    try:
        __import__(mod)
    except ImportError:
        print(f"📦 Installing missing package runtime: {pkg}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

# --- IMPORTS ---
import requests
from bs4 import BeautifulSoup
import firebase_admin
from firebase_admin import credentials, messaging


def extract_qualifications_from_clean_content(content_text, title_text=""):
    """ Strict Multilingual Qualification Extractor with Zero False Positives """
    if not content_text:
        return ["Any / General"]
    
    qualifications = set()
    full_text = f"{title_text} {content_text}"
    text_lower = full_text.lower()
    
    rules = [
        ("10th Pass", [r'\b10\s*th\b', r'\bssc\b', r'दहावी', r'१०\s*वी', r'\b10\s*vi\b']),
        ("12th Pass", [r'\b12\s*th\b', r'\bhsc\b', r'बारावी', r'१२\s*वी', r'\b12\s*vi\b']),
        ("ITI", [r'\biti\b', r'आयटीआय']),
        ("Diploma", [r'\bdiploma\b', r'डिप्लोमा', r'पदविका', r'\bpolytechnic\b']),
        ("Graduate", [r'\bgraduate\b', r'पदवीधर', r'\bbachelor\b', r'\bba\b', r'\bbsc\b', r'\bbcom\b']),
        ("Post Graduate", [r'\bpost\s*graduate\b', r'\bpg\b', r'पदव्युत्तर', r'\bma\b', r'\bmsc\b', r'\bmcom\b']),
        ("MBBS", [r'\bmbbs\b']),
        ("BAMS", [r'\bbams\b']),
        ("BHMS", [r'\bbhms\b']),
        ("B.Tech / B.E", [r'\bb\s*tech\b', r'\bbe\b', r'इंजिनिअरिंग']),
        ("M.Tech / M.E", [r'\bm\s*tech\b', r'\bme\b']),
        ("LLB / Law", [r'\bllb\b', r'\bl\.l\.b\b', r'\blaw\b', r'\blegal\b', r'वकील', r'कायदा']),
        ("B.Ed / D.Ed", [r'\bb\.?\s*ed\b', r'\bd\.?\s*ed\b', r'\btet\b', r'\bctet\b']),
        ("Nursing", [r'\bgnm\b', r'\banm\b', r'\bnursing\b', r'परिचारिका']),
        ("Pharmacy", [r'\bb\.?\s*pharm\b', r'\bd\.?\s*pharm\b', r'\bpharmacy\b', r'फार्मसी']),
        ("CA / CS", [r'\bca\b', r'\bcs\b', r'\bicwa\b']),
        ("AFCAT / Defense", [r'\bafcat\b', r'\bnda\b', r'\bcds\b', r'\barmy\b', r'\bnavy\b', r'\bairforce\b'])
    ]

    for qual_name, patterns in rules:
        for pat in patterns:
            if re.search(pat, text_lower, re.IGNORECASE):
                qualifications.add(qual_name)
                break

    if not qualifications:
        qualifications.add("Any / General")

    return list(qualifications)


def extract_from_srcset(srcset_str):
    if not srcset_str:
        return None
    try:
        sources = [s.strip().split(' ')[0] for s in srcset_str.split(',') if s.strip()]
        if sources:
            return sources[-1]
    except Exception:
        pass
    return None


def extract_real_image_from_card(element):
    if not element:
        return None
    img_tag = element.find('img') if element.name != 'img' else element
    if not img_tag:
        return None

    raw_url = (
        img_tag.get('data-src') or 
        img_tag.get('data-lazy-src') or 
        img_tag.get('data-orig-file') or 
        img_tag.get('src')
    )

    if (not raw_url or "blank.gif" in raw_url or "placeholder" in raw_url):
        raw_url = extract_from_srcset(img_tag.get('srcset') or img_tag.get('data-srcset'))

    return raw_url


def deep_scrape_image_from_page(page_url, headers):
    try:
        res = requests.get(page_url, headers=headers, timeout=5)
        if res.status_code != 200:
            return None
        
        soup = BeautifulSoup(res.text, 'html.parser')

        og_img = soup.find('meta', property=re.compile(r'^og:image$', re.I)) or soup.find('meta', attrs={'name': re.compile(r'^og:image$', re.I)})
        if og_img and og_img.get('content'):
            return og_img['content']

        tw_img = soup.find('meta', attrs={'name': re.compile(r'twitter:image', re.I)})
        if tw_img and tw_img.get('content'):
            return tw_img['content']

        for script in soup.find_all('script', type='application/ld+json'):
            if script.string:
                try:
                    data = json.loads(script.string)
                    items = data.get('@graph', [data]) if isinstance(data, dict) else data
                    if isinstance(items, list):
                        for item in items:
                            if isinstance(item, dict) and 'image' in item:
                                img_val = item['image']
                                if isinstance(img_val, str):
                                    return img_val
                                elif isinstance(img_val, dict) and 'url' in img_val:
                                    return img_val['url']
                                elif isinstance(img_val, list) and len(img_val) > 0:
                                    return img_val[0]
                except Exception:
                    continue

        content_div = soup.find(['div', 'article', 'main'], class_=re.compile(r'content|entry|post|body|article', re.I))
        if content_div:
            img_tag = content_div.find('img')
            if img_tag:
                found_url = (
                    img_tag.get('data-src') or 
                    img_tag.get('data-lazy-src') or 
                    img_tag.get('src') or 
                    extract_from_srcset(img_tag.get('srcset'))
                )
                if found_url and not any(x in found_url.lower() for x in ["blank.gif", "placeholder", "avatar"]):
                    return found_url

    except Exception:
        pass

    return None


def fetch_jobs_from_url(url, default_category, headers):
    jobs_list = []
    try:
        response = requests.get(url, headers=headers, timeout=12)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for a_tag in soup.find_all('a', href=True):
                title = a_tag.text.strip()
                link = a_tag['href']
                
                if len(title) < 15 or not any(k in title for k in ["भरती", "MPSC", "जाहिरात", "Hall Ticket", "प्रवेशपत्र", "निकाल", "Result", "उत्तरतालिका", "वेळापत्रक", "Bharti"]):
                    continue
                if "/category/" in link or link.endswith(".in/") or link == "https://www.majhinaukri.in/":
                    continue

                category = default_category
                if any(k in title for k in ["Hall Ticket", "प्रवेशपत्र", "वेळापत्रक"]):
                    category = "hall_ticket"
                elif any(k in title for k in ["निकाल", "Result", "उत्तरतालिका"]):
                    category = "result"

                img_src = None
                parent = a_tag.find_parent(['article', 'div', 'li', 'section', 'tr'])
                if parent:
                    img_src = extract_real_image_from_card(parent)

                if not img_src or any(x in img_src.lower() for x in ["placeholder", "blank.gif", "avatar"]):
                    img_src = deep_scrape_image_from_page(link, headers)

                if img_src and not any(x in img_src.lower() for x in ["placeholder", "blank.gif", "avatar", "default"]):
                    img_src = img_src.split('?')[0]
                    if img_src.startswith('//'):
                        img_src = "https:" + img_src
                    elif img_src.startswith('/'):
                        img_src = "https://www.majhinaukri.in" + img_src
                    elif img_src.startswith('http://'):
                        img_src = img_src.replace('http://', 'https://')
                else:
                    img_src = ""

                last_date = "तपशील पहा"
                qualifications_list = ["Any / General"]
                
                try:
                    sub_res = requests.get(link, headers=headers, timeout=5)
                    if sub_res.status_code == 200:
                        sub_soup = BeautifulSoup(sub_res.text, 'html.parser')
                        article_content = sub_soup.find(['div', 'article'], class_=re.compile(r'entry-content|post-content|article-body|entry-content-single', re.I))
                        
                        if not article_content:
                            article_content = sub_soup.find('main') or sub_soup.body

                        if article_content:
                            for element in article_content.find_all(['aside', 'nav', 'footer', 'header', 'script', 'style', 'div'], class_=re.compile(r'sidebar|widget|footer|menu|related', re.I)):
                                element.decompose()

                            content_text = article_content.get_text()

                            date_pattern = r'(?:अर्ज\s*करण्याची\s*शेवटची\s*तारीख|ऑनलाइन\s*अर्ज\s*करण्याची\s*शेवटची\s*तारीख|अंतिम\s*तारीख|परीक्षा\s*तारीख|Last\s*Date)\s*[:\-]\s*([^\n\r<]{3,35})'
                            date_match = re.search(date_pattern, content_text, re.IGNORECASE)
                            if date_match:
                                extracted_date = date_match.group(1).strip()
                                extracted_date = re.sub(r'(पर्यंत|आहे|\.|<.*?>)', '', extracted_date).strip()
                                if len(extracted_date) > 2:
                                    last_date = extracted_date[:30]
                            else:
                                fallback_date = re.search(r'(\d{1,2}\s*(?:जानेवारी|फेब्रुवारी|मार्च|एप्रिल|मे|जून|जुलै|ऑगस्ट|सप्टेंबर|ऑक्टोबर|नोव्हेंबर|डिसेंबर|\/\d{1,2}\/|\-\d{1,2}\-)\s*\d{2,4})', content_text)
                                if fallback_date:
                                    last_date = fallback_date.group(0)

                            qualifications_list = extract_qualifications_from_clean_content(content_text, title)

                except Exception:
                    pass

                jobs_list.append({
                    "title": title,
                    "source_url": link,
                    "thumbnail_url": img_src,
                    "category": category,
                    "last_date": last_date,
                    "qualification": qualifications_list
                })

                if len(jobs_list) >= 15:
                    break
    except Exception as e:
        print(f"Error: {e}")

    return jobs_list


def init_firebase_admin():
    """ Initialize Firebase Admin SDK safely """
    try:
        if not firebase_admin._apps:
            cred_json_str = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
            if cred_json_str:
                cred_dict = json.loads(cred_json_str)
                cred = credentials.Certificate(cred_dict)
            elif os.path.exists("firebase_credentials.json"):
                cred = credentials.Certificate("firebase_credentials.json")
            else:
                print("⚠️ No Firebase Service Account credentials found!")
                return False
            firebase_admin.initialize_app(cred)
        return True
    except Exception as e:
        print(f"⚠️ Firebase Admin initialization error: {e}")
        return False


def save_jobs_to_supabase(unique_jobs):
    """ ☁️ Save scraped jobs directly to Supabase cloud table (posts) """
    SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip('/')
    SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

    if not SUPABASE_URL or not SUPABASE_KEY:
        print("⚠️ Supabase credentials missing. Skipping cloud sync.")
        return

    print("☁️ Syncing scraped jobs with Supabase database...")
    rest_url = f"{SUPABASE_URL}/rest/v1/posts"
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates"
    }

    for job in unique_jobs:
        payload = {
            "title": job["title"],
            "source_url": job["source_url"],
            "thumbnail_url": job["thumbnail_url"],
            "category": job["category"],
            "last_date": job["last_date"]
        }
        try:
            requests.post(rest_url, headers=headers, json=payload, timeout=5)
        except Exception:
            pass
    print("✅ Supabase cloud sync completed!")


def send_push_notification_for_new_job(job_title, job_url):
    """ Fetch active device tokens from Supabase REST API and broadcast FCM notification """
    print("🚀 Triggering Instant FCM Push Notification via Supabase REST & Firebase Admin SDK...")
    
    SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip('/')
    SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

    if not SUPABASE_URL or not SUPABASE_KEY:
        print("⚠️ Supabase credentials missing. Skipping push notification.")
        return

    if not init_firebase_admin():
        print("⚠️ Firebase Admin SDK initialization failed. Skipping push notification.")
        return

    try:
        rest_url = f"{SUPABASE_URL}/rest/v1/push_tokens?select=token"
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(rest_url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"❌ Failed to fetch tokens from Supabase REST API: {response.text}")
            return

        tokens_data = response.json()
        if not tokens_data:
            print("⚠️ No push tokens registered in Supabase.")
            return

        tokens = list(set([item["token"] for item in tokens_data if item.get("token")]))
        print(f"📱 Broadcasting notification to {len(tokens)} registered devices...")

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
        print(f"❌ Error broadcasting push notification: {e}")


def main():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    all_jobs = []
    print("Scraping New Ads...")
    all_jobs.extend(fetch_jobs_from_url("https://www.majhinaukri.in/", "advertisement", headers))
    
    print("Scraping Hall Tickets...")
    all_jobs.extend(fetch_jobs_from_url("https://www.majhinaukri.in/hallticket/", "hall_ticket", headers))
    
    print("Scraping Results...")
    all_jobs.extend(fetch_jobs_from_url("https://www.majhinaukri.in/result/", "result", headers))

    unique_jobs = list({job['source_url']: job for job in all_jobs}.values())

    old_jobs = []
    if os.path.exists("jobs.json"):
        try:
            with open("jobs.json", "r", encoding="utf-8") as f:
                old_jobs = json.load(f)
        except Exception:
            old_jobs = []

    old_urls = set(j.get('source_url') for j in old_jobs)
    new_jobs_found = [j for j in unique_jobs if j.get('source_url') not in old_urls]

    with open("jobs.json", "w", encoding="utf-8") as f:
        json.dump(unique_jobs, f, ensure_ascii=False, indent=4)
        
    print(f"Total jobs saved locally: {len(unique_jobs)}")

    # 1. Pahile jobs Supabase cloud var save kara
    save_jobs_to_supabase(unique_jobs)

    # 2. ATA HA TUMI VICHARLELA CODE ITHE EXACTLY PLACE KARA:
    if new_jobs_found:
        print(f"🎉 Found {len(new_jobs_found)} new job(s)!")
        for job in new_jobs_found:
            send_push_notification_for_new_job(job["title"], job["source_url"])
    elif unique_jobs:
        print("ℹ️ No new jobs found compared to last run. Sending latest job alert for testing.")
        latest_job = unique_jobs[0]
        send_push_notification_for_new_job(latest_job["title"], latest_job["source_url"])


if __name__ == "__main__":
    main()

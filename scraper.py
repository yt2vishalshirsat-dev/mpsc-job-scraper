import json
import re
import requests
from bs4 import BeautifulSoup

def scrape_mpsc_jobs():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    jobs_list = []

    try:
        url = "https://www.majhinaukri.in/"
        response = requests.get(url, headers=headers, timeout=12)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Target post list cards on Homepage
            post_cards = soup.find_all(['article', 'div'], class_=['post', 'post-outer', 'entry-card', 'type-post'])

            if not post_cards:
                post_cards = soup.find_all('div', class_=re.compile(r'post|entry|card|item'))

            for card in post_cards:
                # 1. Find Title & Link
                a_tag = card.find('a', href=True)
                if not a_tag:
                    continue
                
                title = a_tag.text.strip()
                link = a_tag['href']
                
                # Filter out menu links and non-job categories
                if len(title) < 18 or not any(k in title for k in ["भरती", "MPSC", "जाहिरात", "Hall Ticket", "निकाल", "Bharti", "Result"]):
                    continue
                if "current-recruitment" in link or "/category/" in link or link.endswith(".in/"):
                    continue

                # 2. Extract Exact Thumbnail Image
                img_src = None
                img_tag = card.find('img')
                
                if img_tag:
                    img_src = (
                        img_tag.get('data-src') or 
                        img_tag.get('data-lazy-src') or 
                        img_tag.get('src')
                    )
                    
                    if not img_src and img_tag.get('srcset'):
                        img_src = img_tag.get('srcset').split(',')[0].split(' ')[0]

                # Clean & Normalize Image URL for Android
                fallback_img = "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e4/Seal_of_Maharashtra.svg/200px-Seal_of_Maharashtra.svg.png"
                
                if not img_src or "via.placeholder" in img_src or "blank.gif" in img_src:
                    img_src = fallback_img
                else:
                    # Remove query params like ?w=150&ssl=1
                    img_src = img_src.split('?')[0]
                    if img_src.startswith('//'):
                        img_src = "https:" + img_src
                    elif img_src.startswith('/'):
                        img_src = "https://www.majhinaukri.in" + img_src
                    elif img_src.startswith('http://'):
                        img_src = img_src.replace('http://', 'https://')

                # 3. Determine Category
                category = "advertisement"
                if any(k in title for k in ["Hall Ticket", "प्रवेशपत्र"]):
                    category = "hall_ticket"
                elif any(k in title for k in ["निकाल", "Result", "उत्तरतालिका"]):
                    category = "result"

                # 4. Fetch Article Page ONLY for exact "Last Date"
                last_date = "जाहिरात पहा"
                try:
                    sub_res = requests.get(link, headers=headers, timeout=5)
                    if sub_res.status_code == 200:
                        sub_soup = BeautifulSoup(sub_res.text, 'html.parser')
                        page_text = sub_soup.get_text()

                        date_pattern = r'(?:अर्ज\s*करण्याची\s*शेवटची\s*तारीख|ऑनलाइन\s*अर्ज\s*करण्याची\s*शेवटची\s*तारीख|अंतिम\s*तारीख|Last\s*Date)\s*[:\-]\s*([^\n\r<]{3,35})'
                        date_match = re.search(date_pattern, page_text, re.IGNORECASE)

                        if date_match:
                            extracted_date = date_match.group(1).strip()
                            extracted_date = re.sub(r'(पर्यंत|आहे|\.|<.*?>)', '', extracted_date).strip()
                            if len(extracted_date) > 2:
                                last_date = extracted_date[:30]
                        else:
                            fallback_date = re.search(r'(\d{1,2}\s*(?:जानेवारी|फेब्रुवारी|मार्च|एप्रिल|मे|जून|जुलै|ऑगस्ट|सप्टेंबर|ऑक्टोबर|नोव्हेंबर|डिसेंबर|\/\d{1,2}\/|\-\d{1,2}\-)\s*\d{2,4})', page_text)
                            if fallback_date:
                                last_date = fallback_date.group(0)
                except Exception:
                    pass

                jobs_list.append({
                    "title": title,
                    "source_url": link,
                    "thumbnail_url": img_src,
                    "category": category,
                    "last_date": last_date
                })

                if len(jobs_list) >= 20:
                    break

    except Exception as e:
        print(f"Scraping error: {e}")

    # Remove duplicates based on source_url
    unique_jobs = list({job['source_url']: job for job in jobs_list}.values())

    # Save cleanly to jobs.json
    with open("jobs.json", "w", encoding="utf-8") as f:
        json.dump(unique_jobs, f, ensure_ascii=False, indent=4)
        
    print(f"Successfully processed {len(unique_jobs)} clean job entries!")

if __name__ == "__main__":
    scrape_mpsc_jobs()

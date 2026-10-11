import json
import re
import requests
from bs4 import BeautifulSoup

def fetch_category_jobs(url, default_category, headers):
    jobs_list = []
    try:
        response = requests.get(url, headers=headers, timeout=12)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find post cards or list containers
            post_cards = soup.find_all(['article', 'div'], class_=['post', 'post-outer', 'entry-card', 'type-post'])
            if not post_cards:
                post_cards = soup.find_all('div', class_=re.compile(r'post|entry|card|item'))

            for card in post_cards:
                a_tag = card.find('a', href=True)
                if not a_tag:
                    continue
                
                title = a_tag.text.strip()
                link = a_tag['href']
                
                # Filter out irrelevant header menu links
                if len(title) < 12 or "current-recruitment" in link or "/category/" in link:
                    continue
                if link.endswith(".in/") or link == "https://www.majhinaukri.in":
                    continue

                # Determine dynamic category if not strictly default
                category = default_category
                if any(k in title for k in ["Hall Ticket", "प्रवेशपत्र", "वेळापत्रक"]):
                    category = "hall_ticket"
                elif any(k in title for k in ["निकाल", "Result", "उत्तरतालिका"]):
                    category = "result"

                # Extract Thumbnail Image
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

                # Standardize Image URL
                fallback_img = "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e4/Seal_of_Maharashtra.svg/200px-Seal_of_Maharashtra.svg.png"
                if not img_src or "via.placeholder" in img_src or "blank.gif" in img_src:
                    img_src = fallback_img
                else:
                    img_src = img_src.split('?')[0]
                    if img_src.startswith('//'):
                        img_src = "https:" + img_src
                    elif img_src.startswith('/'):
                        img_src = "https://www.majhinaukri.in" + img_src
                    elif img_src.startswith('http://'):
                        img_src = img_src.replace('http://', 'https://')

                # Deep Scrape for Last Date / Important Date
                last_date = "तपशील पहा"
                try:
                    sub_res = requests.get(link, headers=headers, timeout=4)
                    if sub_res.status_code == 200:
                        sub_soup = BeautifulSoup(sub_res.text, 'html.parser')
                        page_text = sub_soup.get_text()

                        date_pattern = r'(?:अर्ज\s*करण्याची\s*शेवटची\s*तारीख|ऑनलाइन\s*अर्ज\s*करण्याची\s*शेवटची\s*तारीख|अंतिम\s*तारीख|परीक्षा\s*तारीख|Last\s*Date)\s*[:\-]\s*([^\n\r<]{3,35})'
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

                if len(jobs_list) >= 12: # Limit per section
                    break

    except Exception as e:
        print(f"Error scraping {url}: {e}")

    return jobs_list

def scrape_all_mpsc_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    all_jobs = []

    # 1. Scrape Advertisements (Homepage)
    print("Scraping New Advertisements...")
    all_jobs.extend(fetch_category_jobs("https://www.majhinaukri.in/", "advertisement", headers))

    # 2. Scrape Hall Tickets & Timetables
    print("Scraping Hall Tickets & Timetables...")
    all_jobs.extend(fetch_category_jobs("https://www.majhinaukri.in/hallticket/", "hall_ticket", headers))

    # 3. Scrape Results & Answer Keys
    print("Scraping Results & Answer Keys...")
    all_jobs.extend(fetch_category_jobs("https://www.majhinaukri.in/result/", "result", headers))

    # Remove duplicate entries based on source_url
    unique_jobs = list({job['source_url']: job for job in all_jobs}.values())

    # Save to jobs.json
    with open("jobs.json", "w", encoding="utf-8") as f:
        json.dump(unique_jobs, f, ensure_ascii=False, indent=4)

    print(f"Successfully scraped & saved total {len(unique_jobs)} items across all categories!")

if __name__ == "__main__":
    scrape_all_mpsc_data()

import json
import re
import requests
from bs4 import BeautifulSoup

def extract_real_image_url(element):
    """ Helper function to extract exact highest-resolution image URL from any HTML tag """
    if not element:
        return None
        
    img_tag = element.find('img') if element.name != 'img' else element
    if not img_tag:
        return None

    # Check all possible lazy-load & standard src attributes used by WordPress/CDNs
    raw_url = (
        img_tag.get('data-src') or 
        img_tag.get('data-lazy-src') or 
        img_tag.get('data-orig-file') or 
        img_tag.get('src')
    )

    # Parse srcset if direct src is missing or standard placeholder
    if (not raw_url or "blank.gif" in raw_url or "placeholder" in raw_url) and (img_tag.get('srcset') or img_tag.get('data-srcset')):
        srcset = img_tag.get('srcset') or img_tag.get('data-srcset')
        # Take the first or highest res URL from srcset entry (URL [resolution])
        sources = [s.strip().split(' ')[0] for s in srcset.split(',') if s.strip()]
        if sources:
            raw_url = sources[-1] # Usually last or first is highest res

    return raw_url

def fetch_jobs_from_url(url, default_category, headers):
    jobs_list = []
    try:
        response = requests.get(url, headers=headers, timeout=12)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for a_tag in soup.find_all('a', href=True):
                title = a_tag.text.strip()
                link = a_tag['href']
                
                # Filter irrelevant header/navigation links
                if len(title) < 15 or not any(k in title for k in ["भरती", "MPSC", "जाहिरात", "Hall Ticket", "प्रवेशपत्र", "निकाल", "Result", "उत्तरतालिका", "वेळापत्रक", "Bharti"]):
                    continue
                if "/category/" in link or link.endswith(".in/") or link == "https://www.majhinaukri.in/":
                    continue

                # Category determine karne
                category = default_category
                if any(k in title for k in ["Hall Ticket", "प्रवेशपत्र", "वेळापत्रक"]):
                    category = "hall_ticket"
                elif any(k in title for k in ["निकाल", "Result", "उत्तरतालिका"]):
                    category = "result"

                # --- 1. REAL IMAGE EXTRACTOR FROM CONTAINER CARD ---
                img_src = None
                parent = a_tag.find_parent(['article', 'div', 'li', 'section', 'tr'])
                
                if parent:
                    img_src = extract_real_image_url(parent)

                # --- 2. DEEP SCRAPE ARTICLE PAGE IF HOMEPAGE HAS NO IMAGE ---
                if not img_src or any(x in img_src.lower() for x in ["placeholder", "blank.gif", "avatar"]):
                    try:
                        sub_img_res = requests.get(link, headers=headers, timeout=4)
                        if sub_img_res.status_code == 200:
                            sub_img_soup = BeautifulSoup(sub_img_res.text, 'html.parser')
                            # Look for article banner/first content image
                            content_div = sub_img_soup.find(['div', 'article', 'main'], class_=re.compile(r'content|entry|post|body|article'))
                            if content_div:
                                img_src = extract_real_image_url(content_div)
                    except Exception:
                        pass

                # Clean & Normalize Real Image URL
                default_emblem = "https://upload.wikimedia.org/wikipedia/commons/e/e4/Seal_of_Maharashtra.png"
                
                if img_src and not any(x in img_src.lower() for x in ["placeholder", "blank.gif", "avatar", "default"]):
                    # Strip URL parameters like ?w=150&ssl=1
                    img_src = img_src.split('?')[0]
                    if img_src.startswith('//'):
                        img_src = "https:" + img_src
                    elif img_src.startswith('/'):
                        img_src = "https://www.majhinaukri.in" + img_src
                    elif img_src.startswith('http://'):
                        img_src = img_src.replace('http://', 'https://')
                else:
                    img_src = default_emblem

                # --- 3. LAST DATE / EXAM DATE DEEP SCRAPE ---
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

                if len(jobs_list) >= 15:
                    break
    except Exception as e:
        print(f"Error: {e}")

    return jobs_list

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

    # Remove duplicates
    unique_jobs = list({job['source_url']: job for job in all_jobs}.values())

    with open("jobs.json", "w", encoding="utf-8") as f:
        json.dump(unique_jobs, f, ensure_ascii=False, indent=4)
        
    print(f"Total jobs saved: {len(unique_jobs)}")

if __name__ == "__main__":
    main()

import json
import re
import requests
from bs4 import BeautifulSoup

def extract_from_srcset(srcset_str):
    """ Extract highest resolution image URL from srcset string """
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
    """ Level 1: Extract image from listing card elements """
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
    """ Deep Scrape Engine: Checks Meta Tags, JSON-LD, and Article Body """
    try:
        res = requests.get(page_url, headers=headers, timeout=5)
        if res.status_code != 200:
            return None
        
        soup = BeautifulSoup(res.text, 'html.parser')

        # Level 2: OpenGraph Meta Tag (Highest Accuracy for WordPress/MajhiNaukri)
        og_img = soup.find('meta', property=re.compile(r'^og:image$', re.I)) or soup.find('meta', attrs={'name': re.compile(r'^og:image$', re.I)})
        if og_img and og_img.get('content'):
            return og_img['content']

        # Level 3: Twitter Image Meta Tag
        tw_img = soup.find('meta', attrs={'name': re.compile(r'twitter:image', re.I)})
        if tw_img and tw_img.get('content'):
            return tw_img['content']

        # Level 4: Schema JSON-LD Metadata
        for script in soup.find_all('script', type='application/ld+json'):
            if script.string:
                try:
                    data = json.loads(script.string)
                    # Handle single object or @graph array
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

        # Level 5: First Content Image inside article post body
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
                
                # Filter irrelevant links
                if len(title) < 15 or not any(k in title for k in ["भरती", "MPSC", "जाहिरात", "Hall Ticket", "प्रवेशपत्र", "निकाल", "Result", "उत्तरतालिका", "वेळापत्रक", "Bharti"]):
                    continue
                if "/category/" in link or link.endswith(".in/") or link == "https://www.majhinaukri.in/":
                    continue

                category = default_category
                if any(k in title for k in ["Hall Ticket", "प्रवेशपत्र", "वेळापत्रक"]):
                    category = "hall_ticket"
                elif any(k in title for k in ["निकाल", "Result", "उत्तरतालिका"]):
                    category = "result"

                # Step 1: Extract from Card
                img_src = None
                parent = a_tag.find_parent(['article', 'div', 'li', 'section', 'tr'])
                if parent:
                    img_src = extract_real_image_from_card(parent)

                # Step 2: Deep Scrape if card image missing or invalid
                if not img_src or any(x in img_src.lower() for x in ["placeholder", "blank.gif", "avatar"]):
                    img_src = deep_scrape_image_from_page(link, headers)

                # Step 3: Clean URL Format
                if img_src and not any(x in img_src.lower() for x in ["placeholder", "blank.gif", "avatar", "default"]):
                    img_src = img_src.split('?')[0] # Strip CDN URL params
                    if img_src.startswith('//'):
                        img_src = "https:" + img_src
                    elif img_src.startswith('/'):
                        img_src = "https://www.majhinaukri.in" + img_src
                    elif img_src.startswith('http://'):
                        img_src = img_src.replace('http://', 'https://')
                else:
                    img_src = ""

                # Step 4: Last Date Scrape
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

    unique_jobs = list({job['source_url']: job for job in all_jobs}.values())

    with open("jobs.json", "w", encoding="utf-8") as f:
        json.dump(unique_jobs, f, ensure_ascii=False, indent=4)
        
    print(f"Total jobs saved: {len(unique_jobs)}")

if __name__ == "__main__":
    main()

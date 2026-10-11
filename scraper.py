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
            
            # Find all potential article links
            anchors = soup.find_all('a', href=True)

            for a in anchors:
                title = a.text.strip()
                link = a['href']
                
                # Filter out menu links and category pages
                if len(title) > 18 and any(k in title for k in ["भरती", "MPSC", "जाहिरात", "Hall Ticket", "निकाल", "Bharti", "Result"]):
                    if "current-recruitment" in link or "/category/" in link or link.endswith(".in/"):
                        continue # Skip main index/category URLs
                    
                    category = "advertisement"
                    if any(k in title for k in ["Hall Ticket", "प्रवेशपत्र"]):
                        category = "hall_ticket"
                    elif any(k in title for k in ["निकाल", "Result", "उत्तरतालिका"]):
                        category = "result"

                    # Fallback standard MPSC seal icon if image is missing
                    img_src = "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e4/Seal_of_Maharashtra.svg/200px-Seal_of_Maharashtra.svg.png"
                    last_date = "जाहिरात पहा"

                    # --- DEEP SCRAPE ARTICLE PAGE ---
                    try:
                        sub_res = requests.get(link, headers=headers, timeout=6)
                        if sub_res.status_code == 200:
                            sub_soup = BeautifulSoup(sub_res.text, 'html.parser')
                            
                            # 1. Fetch Real Article Thumbnail (Handling Lazy Loading)
                            post_content = sub_soup.find(['div', 'article'], class_=['entry-content', 'post-body', 'item-content', 'post-content'])
                            if post_content:
                                img_tag = post_content.find('img')
                                if img_tag:
                                    img_src = img_tag.get('data-lazy-src') or img_tag.get('data-src') or img_tag.get('src') or img_src

                            # Clean relative image paths
                            if img_src and img_src.startswith('/'):
                                img_src = "https://www.majhinaukri.in" + img_src

                            # 2. Extract Last Date (Marathi + English Patterns)
                            page_text = sub_soup.get_text()
                            
                            # Regex Pattern for Marathi & English "Last Date / अर्ज करण्याची शेवटची तारीख"
                            date_pattern = r'(?:अर्ज\s*करण्याची\s*शेवटची\s*तारीख|ऑनलाइन\s*अर्ज\s*करण्याची\s*शेवटची\s*तारीख|अंतिम\s*तारीख|Last\s*Date)\s*[:\-]\s*([^\n\r<]{3,35})'
                            date_match = re.search(date_pattern, page_text, re.IGNORECASE)

                            if date_match:
                                extracted_date = date_match.group(1).strip()
                                # Clean up unwanted extra symbols/text
                                extracted_date = re.sub(r'(पर्यंत|आहे|\.|<.*?>)', '', extracted_date).strip()
                                if len(extracted_date) > 2:
                                    last_date = extracted_date[:30]
                            else:
                                # Generic Date Regex (e.g., 15 ऑक्टोबर 2026 or 15/10/2026)
                                fallback_date = re.search(r'(\d{1,2}\s*(?:जानेवारी|फेब्रुवारी|मार्च|एप्रिल|मे|जून|जुलै|ऑगस्ट|सप्टेंबर|ऑक्टोबर|नोव्हेंबर|डिसेंबर|\/\d{1,2}\/|\-\d{1,2}\-)\s*\d{2,4})', page_text)
                                if fallback_date:
                                    last_date = fallback_date.group(0)

                    except Exception as sub_err:
                        print(f"Error deep scraping {link}: {sub_err}")

                    jobs_list.append({
                        "title": title,
                        "source_url": link,
                        "thumbnail_url": img_src,
                        "category": category,
                        "last_date": last_date
                    })

                    # Stop after fetching top 20 items to keep API fast
                    if len(jobs_list) >= 20:
                        break

    except Exception as e:
        print(f"Scraping error: {e}")

    # Remove duplicates
    unique_jobs = list({job['source_url']: job for job in jobs_list}.values())

    # Write to jobs.json
    with open("jobs.json", "w", encoding="utf-8") as f:
        json.dump(unique_jobs, f, ensure_ascii=False, indent=4)
        
    print(f"Successfully processed {len(unique_jobs)} clean job entries!")

if __name__ == "__main__":
    scrape_mpsc_jobs()

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
                
                # Filter out generic menu links and focus ONLY on real recruitment posts
                if len(title) > 20 and any(k in title for k in ["भरती", "MPSC", "जाहिरात", "Hall Ticket", "निकाल", "Bharti", "Result"]):
                    if "current-recruitment" in link or "category" in link:
                        continue # Skip category/menu pages
                    
                    # Determine category
                    category = "advertisement"
                    if any(k in title for k in ["Hall Ticket", "प्रवेशपत्र"]):
                        category = "hall_ticket"
                    elif any(k in title for k in ["निकाल", "Result", "उत्तरतालिका"]):
                        category = "result"

                    # Default high-quality standard government emblem fallback image
                    img_src = "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e4/Seal_of_Maharashtra.svg/200px-Seal_of_Maharashtra.svg.png"
                    last_date = "अधिकृत जाहिरात पहा"

                    # DEEP SCRAPE: Fetch the inner article page for Real Image & Last Date
                    try:
                        sub_res = requests.get(link, headers=headers, timeout=5)
                        if sub_res.status_code == 200:
                            sub_soup = BeautifulSoup(sub_res.text, 'html.parser')
                            
                            # Extract post content image
                            post_img = sub_soup.find('div', class_=['entry-content', 'post-body', 'post-content'])
                            if post_img:
                                img_tag = post_img.find('img')
                                if img_tag:
                                    img_src = img_tag.get('src') or img_tag.get('data-src') or img_src

                            # Extract Last Date from page text or table
                            page_text = sub_res.text
                            date_match = re.search(r'(अंतिम तारीख|शेवटची तारीख|Last Date)\s*[:\-]\s*([\d\w\s\/\-]+)', page_text)
                            if date_match:
                                last_date = date_match.group(2).strip()[:25]
                            else:
                                raw_date = re.search(r'(\d{1,2}\s*(?:जानेवारी|फेब्रुवारी|मार्च|एप्रिल|मे|जून|जुलै|ऑगस्ट|सप्टेंबर|ऑक्टोबर|नोव्हेंबर|डिसेंबर|\/\d{1,2}\/|\-\d{1,2}\-)\s*\d{2,4})', page_text)
                                if raw_date:
                                    last_date = raw_date.group(0)
                    except Exception as e:
                        pass # Use fallbacks if detail page times out

                    jobs_list.append({
                        "title": title,
                        "source_url": link,
                        "thumbnail_url": img_src,
                        "category": category,
                        "last_date": last_date
                    })

                    # Limit total items for instant loading
                    if len(jobs_list) >= 25:
                        break

    except Exception as e:
        print(f"Scraping error: {e}")

    # Deduplicate entries by link
    unique_jobs = list({job['source_url']: job for job in jobs_list}.values())

    # Write cleanly to jobs.json
    with open("jobs.json", "w", encoding="utf-8") as f:
        json.dump(unique_jobs, f, ensure_ascii=False, indent=4)
        
    print(f"Successfully processed {len(unique_jobs)} clean job entries!")

if __name__ == "__main__":
    scrape_mpsc_jobs()

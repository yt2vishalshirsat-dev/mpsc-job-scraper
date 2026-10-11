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
            
            # Find posts/articles on the homepage
            posts = soup.find_all(['article', 'div'], class_=['post', 'post-outer', 'entry-header', 'entry-card'])
            
            # Fallback to general link iteration if specific post containers aren't found
            if not posts:
                posts = soup.find_all('a', href=True)

            for post in posts:
                # 1. Extract Title & Link
                if post.name == 'a':
                    title = post.text.strip()
                    link = post['href']
                    img_src = "https://images.unsplash.com/photo-1586281380349-632531db7ed4?w=200" # Default MPSC news fallback
                else:
                    a_tag = post.find('a', href=True)
                    if not a_tag:
                        continue
                    title = a_tag.text.strip()
                    link = a_tag['href']
                    
                    # 2. Extract Real Thumbnail
                    img_tag = post.find('img')
                    if img_tag:
                        img_src = img_tag.get('src') or img_tag.get('data-src') or img_tag.get('data-lazy-src')
                    else:
                        img_src = "https://images.unsplash.com/photo-1586281380349-632531db7ed4?w=200"

                # Filter valid posts only
                if len(title) > 15 and any(k in title for k in ["भरती", "MPSC", "जाहिरात", "Hall Ticket", "निकाल", "Bharti", "Result"]):
                    
                    # 3. Categorize
                    category = "advertisement"
                    if any(k in title for k in ["Hall Ticket", "प्रवेशपत्र"]):
                        category = "hall_ticket"
                    elif any(k in title for k in ["निकाल", "Result", "उत्तरतालिका"]):
                        category = "result"

                    # 4. Smart Last Date Extraction (Regex for dates like 15-10-2026 or 15 ऑक्टोबर)
                    date_match = re.search(r'(\d{1,2}\s*(?:जानेवारी|फेब्रुवारी|मार्च|एप्रिल|मे|जून|जुलै|ऑगस्ट|सप्टेंबर|ऑक्टोबर|नोव्हेंबर|डिसेंबर|\/\d{1,2}\/|\-\d{1,2}\-)\s*\d{2,4})', title)
                    if date_match:
                        last_date = date_match.group(0)
                    else:
                        last_date = "जाहिरात पहा"

                    # Clean Thumbnail URL (Handle relative paths)
                    if img_src and img_src.startswith('/'):
                        img_src = "https://www.majhinaukri.in" + img_src

                    jobs_list.append({
                        "title": title,
                        "source_url": link,
                        "thumbnail_url": img_src,
                        "category": category,
                        "last_date": last_date
                    })

    except Exception as e:
        print(f"Scraping error: {e}")

    # Remove duplicates based on source_url
    unique_jobs = {job['source_url']: job for job in jobs_list}.values()
    final_jobs = list(unique_jobs)

    # Save to jobs.json
    with open("jobs.json", "w", encoding="utf-8") as f:
        json.dump(final_jobs, f, ensure_ascii=False, indent=4)
        
    print(f"Successfully saved {len(final_jobs)} items with thumbnails & dates to jobs.json!")

if __name__ == "__main__":
    scrape_mpsc_jobs()

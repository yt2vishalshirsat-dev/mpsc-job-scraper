import json
import requests
from bs4 import BeautifulSoup

def scrape_mpsc_jobs():
    # Example Target: You can loop through your 15 target websites here
    url = "https://www.majhinaukri.in/" 
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    jobs_list = []
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Example parsing logic (adjust selectors based on target site HTML)
            posts = soup.find_all('div', class_='post-outer', limit=15)
            for post in posts:
                title_elem = post.find('h2')
                link_elem = post.find('a')
                img_elem = post.find('img')
                
                if title_elem and link_elem:
                    title = title_elem.text.strip()
                    link = link_elem['href']
                    thumb = img_elem['src'] if img_elem else "https://via.placeholder.com/150"
                    
                    # Simple category logic based on title keywords
                    category = "advertisement"
                    if "hall ticket" in title.lower() or "प्रवेशपत्र" in title:
                        category = "hall_ticket"
                    elif "result" in title.lower() or "निकाल" in title:
                        category = "result"

                    jobs_list.append({
                        "title": title,
                        "source_url": link,
                        "thumbnail_url": thumb,
                        "category": category,
                        "last_date": "तपासा (Check Link)"
                    })
    except Exception as e:
        print(f"Error scraping: {e}")

    # Save data into jobs.json
    with open("jobs.json", "w", encoding="utf-8") as f:
        json.dump(jobs_list, f, ensure_ascii=False, indent=4)
    print("jobs.json generated successfully!")

if __name__ == "__main__":
    scrape_mpsc_jobs()

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
            soup = BeautifulSoup(response.text, 'html.

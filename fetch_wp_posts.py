import os
import requests
import json
from bs4 import BeautifulSoup
from urllib.parse import urlparse

API_URL = 'https://machinekoder.com/wp-json/wp/v2/posts?per_page=100&_embed'
OUTPUT_DIR = 'content/blog'
IMG_BASE_DIR = 'static/blog_images'

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(IMG_BASE_DIR, exist_ok=True)

def fetch_all_posts():
    posts = []
    page = 1
    while True:
        resp = requests.get(f'{API_URL}&page={page}')
        if resp.status_code != 200:
            break
        data = resp.json()
        if not data:
            break
        posts.extend(data)
        page += 1
    return posts

def download_and_relink_images(html, slug):
    soup = BeautifulSoup(html, 'html.parser')
    img_dir = os.path.join(IMG_BASE_DIR, slug)
    os.makedirs(img_dir, exist_ok=True)
    for img in soup.find_all('img'):
        src = img.get('src')
        if not src:
            continue
        img_filename = os.path.basename(urlparse(src).path)
        local_img_path = os.path.join(img_dir, img_filename)
        # Download image if not already present
        if not os.path.exists(local_img_path):
            try:
                resp = requests.get(src, timeout=10)
                if resp.status_code == 200:
                    with open(local_img_path, 'wb') as f:
                        f.write(resp.content)
                    print(f'Downloaded image: {src} -> {local_img_path}')
            except Exception as e:
                print(f'Failed to download image {src}: {e}')
        # Update src to local static path
        img['src'] = f'/static/blog_images/{slug}/{img_filename}'
    return str(soup)

def download_featured_image(post, slug):
    featured_url = ''
    if '_embedded' in post and 'wp:featuredmedia' in post['_embedded']:
        media = post['_embedded']['wp:featuredmedia']
        if media and isinstance(media, list) and 'source_url' in media[0]:
            featured_url = media[0]['source_url']
    if not featured_url:
        return ''
    img_dir = os.path.join(IMG_BASE_DIR, slug)
    os.makedirs(img_dir, exist_ok=True)
    img_filename = os.path.basename(urlparse(featured_url).path)
    local_img_path = os.path.join(img_dir, img_filename)
    if not os.path.exists(local_img_path):
        try:
            resp = requests.get(featured_url, timeout=10)
            if resp.status_code == 200:
                with open(local_img_path, 'wb') as f:
                    f.write(resp.content)
                print(f'Downloaded featured image: {featured_url} -> {local_img_path}')
        except Exception as e:
            print(f'Failed to download featured image {featured_url}: {e}')
    return f'/static/blog_images/{slug}/{img_filename}'

def save_post(post):
    slug = post['slug']
    featured_image = download_featured_image(post, slug)
    meta = {
        'title': post['title']['rendered'],
        'date': post['date'],
        'slug': slug,
        'original_url': post['link'],
        'featured_image': featured_image if featured_image else ''
    }
    content = post['content']['rendered']
    content = download_and_relink_images(content, slug)
    with open(os.path.join(OUTPUT_DIR, f'{slug}.html'), 'w', encoding='utf-8') as f:
        f.write(f'<!--\n{json.dumps(meta, indent=2)}\n-->\n')
        f.write(content)

if __name__ == '__main__':
    posts = fetch_all_posts()
    for post in posts:
        save_post(post)
    print(f'Archived {len(posts)} posts to {OUTPUT_DIR}')

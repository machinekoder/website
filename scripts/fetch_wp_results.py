import os
import requests
from bs4 import BeautifulSoup
import json

RESULTS = [
    {
        'title': 'User-friendly CNC Operator UI',
        'slug': 'user-friendly-cnc-operator-ui',
        'url': 'https://machinekoder.com/case-study/user-friendly-cnc-operator-ui/'
    },
    {
        'title': 'Cross-platform 3D Printer User Interface',
        'slug': 'cross-platform-3d-printer-user-interface',
        'url': 'https://machinekoder.com/case-study/663/'
    },
    {
        'title': 'Mobile App Pendant for CNC Machine',
        'slug': 'mobile-app-pendant-for-cnc-machine',
        'url': 'https://machinekoder.com/case-study/mobile-app-pendant-for-cnc-machine/'
    },
]

OUTPUT_DIR = 'content/results'
IMG_BASE_DIR = 'static/results_images'

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(IMG_BASE_DIR, exist_ok=True)

def download_and_relink_images(html, slug):
    soup = BeautifulSoup(html, 'html.parser')
    img_dir = os.path.join(IMG_BASE_DIR, slug)
    os.makedirs(img_dir, exist_ok=True)
    for img in soup.find_all('img'):
        src = img.get('src')
        if not src:
            continue
        img_filename = os.path.basename(src.split('?')[0])
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
        img['src'] = f'/static/results_images/{slug}/{img_filename}'
    return str(soup)

def save_result(result):
    resp = requests.get(result['url'])
    if resp.status_code != 200:
        print(f"Failed to fetch {result['url']}")
        return
    soup = BeautifulSoup(resp.text, 'html.parser')
    # Try to extract main content (customize as needed)
    main_content = (
        soup.find('main') or
        soup.find('article') or
        soup.find(class_='entry-content') or
        soup.body
    )
    content = download_and_relink_images(str(main_content), result['slug'])
    meta = {
        'title': result['title'],
        'slug': result['slug'],
        'original_url': result['url']
    }
    with open(os.path.join(OUTPUT_DIR, f"{result['slug']}.html"), 'w', encoding='utf-8') as f:
        f.write(f'<!--\n{json.dumps(meta, indent=2)}\n-->\n')
        f.write(content)

if __name__ == '__main__':
    for result in RESULTS:
        save_result(result)
    print(f'Archived {len(RESULTS)} project results to {OUTPUT_DIR}')

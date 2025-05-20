import os
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader
from slugify import slugify
import re
import sys
sys.path.append(str(Path(__file__).parent.parent))
from config import config

BLOG_DIR = Path('content/blog')
RESULTS_DIR = Path('content/results')

class StaticSiteGenerator:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.templates_dir = self.base_dir / "templates"
        self.static_dir = self.base_dir / "static"
        self.output_dir = self.base_dir / "output"
        self.blog_posts_dir = self.output_dir
        self.results_dir = self.output_dir / "results"
        
        # Initialize Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=True
        )
        
        # Create necessary directories
        self._create_directories()
        
    def _create_directories(self):
        for directory in [self.templates_dir, self.static_dir, self.output_dir, self.blog_posts_dir, self.results_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _copy_static_files(self):
        """Copy static files to output directory."""
        if self.static_dir.exists():
            shutil.copytree(self.static_dir, self.output_dir / "static", dirs_exist_ok=True)
    
    def _parse_local_html(self, file_path: Path) -> Dict:
        with open(file_path, encoding='utf-8') as f:
            lines = f.readlines()
        # Extract metadata from comment block
        if lines[0].startswith('<!--'):
            meta_lines = []
            i = 1
            while i < len(lines) and not lines[i].startswith('-->'):
                meta_lines.append(lines[i])
                i += 1
            meta = json.loads(''.join(meta_lines))
            content = ''.join(lines[i+1:])
        else:
            meta = {}
            content = ''.join(lines)
        return {'meta': meta, 'content': content}

    def generate_blog_posts(self, config: Dict) -> List[Dict]:
        posts = []
        for file in sorted(BLOG_DIR.glob('*.html')):
            parsed = self._parse_local_html(file)
            meta = parsed['meta']
            content = parsed['content']
            slug = meta.get('slug', file.stem)
            # Handle featured image
            featured_img_tag = ''
            if 'featured_image' in meta and meta['featured_image']:
                featured_img_tag = f'<img class="featured-image" src="{meta["featured_image"]}" alt="Featured image">'
            # Rewrite image sources and prepend featured image if present
            content = featured_img_tag + self._rewrite_image_sources(content, slug)
            # Parse the date and keep both the datetime object and formatted string
            date_obj = datetime.strptime(meta.get('date', '2000-01-01T00:00:00'), '%Y-%m-%dT%H:%M:%S')
            post = {
                'title': meta.get('title', 'Untitled'),
                'content': content,
                'excerpt': self._clean_excerpt(BeautifulSoup(content, 'html.parser').get_text()[:300]),
                'date': date_obj,
                'date_formatted': date_obj.strftime('%B %d, %Y'),
                'slug': slug,
                'original_url': meta.get('original_url', ''),
            }
            # Write blog post HTML
            post_dir = self.blog_posts_dir / post['slug']
            post_dir.mkdir(exist_ok=True)
            template = self.env.get_template('blog_post.html')
            with open(post_dir / 'index.html', 'w', encoding='utf-8') as f:
                f.write(template.render(post=post, config=config, now=datetime.now()))
            posts.append(post)
        return posts

    def generate_results_pages(self, config: Dict) -> List[Dict]:
        projects = []
        for file in sorted(RESULTS_DIR.glob('*.html')):
            parsed = self._parse_local_html(file)
            meta = parsed['meta']
            content = parsed['content']
            project = {
                'title': meta.get('title', 'Untitled'),
                'slug': meta.get('slug', file.stem),
                'content': content,
                'original_url': meta.get('original_url', ''),
            }
            # Rewrite result image links
            content = self._rewrite_result_image_links(content, project['slug'])
            # Write project result HTML
            result_file = self.results_dir / f"{project['slug']}.html"
            template = self.env.get_template('result_post.html')
            with open(result_file, 'w', encoding='utf-8') as f:
                f.write(template.render(project=project, config=config, now=datetime.now()))
            projects.append(project)
        return projects

    def generate_site(self, config: Dict):
        self._copy_static_files()
        # Generate main pages
        pages = ['index.html', 'about.html', 'results.html']
        for page in pages:
            template = self.env.get_template(page)
            with open(self.output_dir / page, 'w', encoding='utf-8') as f:
                f.write(template.render(config=config, now=datetime.now()))
        # Generate blog posts and blog listing page
        posts = self.generate_blog_posts(config)
        template = self.env.get_template('blog.html')
        with open(self.output_dir / 'blog.html', 'w', encoding='utf-8') as f:
            f.write(template.render(config=config, posts=posts, now=datetime.now()))
        # Generate project result detail pages
        projects = self.generate_results_pages(config)
        template = self.env.get_template('results.html')
        with open(self.output_dir / 'results.html', 'w', encoding='utf-8') as f:
            f.write(template.render(config=config, projects=projects, now=datetime.now()))
        print(f"Site generated successfully in {self.output_dir}")

    def _clean_excerpt(self, excerpt: str) -> str:
        # Remove 'x minutes read' and '< 1 minute read' patterns, even if directly followed by text
        excerpt = re.sub(r'(\d+\s*minute(s)?\s*read|<\s*1\s*minute(s)?\s*read)[\s\.:,-]*', '', excerpt, flags=re.IGNORECASE)
        excerpt = re.sub(r'^\s*<\s*', '', excerpt)  # Remove any leading '<' left behind
        excerpt = excerpt.strip()
        if not excerpt.endswith('...'):
            excerpt += '...'
        return excerpt

    def _rewrite_image_sources(self, html: str, slug: str) -> str:
        soup = BeautifulSoup(html, 'html.parser')
        # Remove <a> tags that wrap only an <img>
        for a in soup.find_all('a'):
            if a.find('img') and len(a.contents) == 1 and a.img:
                a.replace_with(a.img)
        for img in soup.find_all('img'):
            src = img.get('src')
            if src and not src.startswith('/static/blog_images/'):
                img_filename = os.path.basename(src.split('?')[0])
                img['src'] = f'/static/blog_images/{slug}/{img_filename}'
            # Remove srcset attribute if present
            if 'srcset' in img.attrs:
                del img['srcset']
        return str(soup)

    def _rewrite_result_image_links(self, html: str, slug: str) -> str:
        soup = BeautifulSoup(html, 'html.parser')
        # Remove <a> tags that contain images
        for a in soup.find_all('a'):
            if a.find('img'):
                a.replace_with(*a.contents)
        # Remove any element with class 'entry-thumb'
        for thumb in soup.select('.entry-thumb'):
            thumb.decompose()
        return str(soup)

if __name__ == "__main__":
    generator = StaticSiteGenerator()
    generator.generate_site(config) 
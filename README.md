# Personal Website Generator

A high-performance static website generator for developers, featuring a futuristic design and WordPress blog post archiving capabilities.

## Features

- 🚀 Lightning-fast static site generation
- 🎨 Modern, futuristic design with dark mode
- 📝 WordPress blog post archiving
- 🔄 Automatic deployment to GitHub Pages
- 📱 Fully responsive design
- 🎯 SEO-friendly
- 🔒 No JavaScript required for content

## Setup

1. Clone this repository:
```bash
git clone https://github.com/yourusername/your-repo-name.git
cd your-repo-name
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your site:
Edit the configuration in `src/generator.py` with your personal information:
```python
config = {
    'name': 'Your Name',
    'title': 'Senior Developer',
    'description': 'Your professional description',
    'wordpress_url': 'https://your-wordpress-site.com',  # Optional
    'social_links': {
        'github': 'https://github.com/yourusername',
        'linkedin': 'https://linkedin.com/in/yourusername',
        'twitter': 'https://twitter.com/yourusername'
    }
}
```

4. Generate the site:
```bash
python src/generator.py
```

5. Preview locally:
The generated site will be in the `output` directory. You can serve it using any static file server.

## Deployment

The site is automatically deployed to GitHub Pages when you push to the main branch. Make sure to:

1. Enable GitHub Pages in your repository settings
2. Select the `gh-pages` branch as the source
3. Push your changes to the main branch

## Customization

- Templates are in the `templates` directory
- Static assets (CSS, images) go in the `static` directory
- Modify the styles in the template files to match your preferences

## Performance Features

- Zero JavaScript for content rendering
- Inline critical CSS
- Optimized asset loading
- Responsive images
- Semantic HTML structure
- Fast initial page load

## License

MIT License - feel free to use this template for your personal website! 
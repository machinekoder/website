from PIL import Image
import os

def optimize_image(input_path, output_path, max_size=(1200, 1200), quality=85):
    # Open the image
    with Image.open(input_path) as img:
        # Convert to RGB if necessary
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        
        # Calculate new dimensions while maintaining aspect ratio
        ratio = min(max_size[0] / img.width, max_size[1] / img.height)
        new_size = (int(img.width * ratio), int(img.height * ratio))
        
        # Resize image
        img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        # Save optimized image
        img.save(output_path, 'WEBP', quality=quality, optimize=True)

def main():
    # Create output directory if it doesn't exist
    os.makedirs('static/images/optimized', exist_ok=True)
    
    # Optimize headshot
    optimize_image(
        'static/images/headshot.png',
        'static/images/optimized/headshot.webp',
        max_size=(1200, 1200)
    )
    
    # Optimize logo
    optimize_image(
        'static/images/logo.png',
        'static/images/optimized/logo.webp',
        max_size=(800, 800)
    )

if __name__ == '__main__':
    main() 
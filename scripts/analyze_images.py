import os
from PIL import Image
import glob

def get_directory_size(path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
    return total_size

def analyze_png_files(directory):
    total_png_size = 0
    total_png_count = 0
    png_files = []
    
    # Find all PNG files
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.png'):
                file_path = os.path.join(root, file)
                file_size = os.path.getsize(file_path)
                total_png_size += file_size
                total_png_count += 1
                png_files.append((file_path, file_size))
    
    # Sort files by size
    png_files.sort(key=lambda x: x[1], reverse=True)
    
    print(f"\nPNG Analysis Results:")
    print(f"Total PNG files found: {total_png_count}")
    print(f"Total PNG size: {total_png_size / 1024 / 1024:.2f} MB")
    print("\nTop 5 largest PNG files:")
    for file_path, size in png_files[:5]:
        print(f"{file_path}: {size / 1024 / 1024:.2f} MB")
    
    # Estimate WebP savings (typically 25-35% smaller than PNG)
    estimated_webp_size = total_png_size * 0.7  # Assuming 30% reduction
    potential_savings = total_png_size - estimated_webp_size
    
    print(f"\nEstimated WebP conversion savings:")
    print(f"Current PNG size: {total_png_size / 1024 / 1024:.2f} MB")
    print(f"Estimated WebP size: {estimated_webp_size / 1024 / 1024:.2f} MB")
    print(f"Potential savings: {potential_savings / 1024 / 1024:.2f} MB (30% reduction)")

if __name__ == '__main__':
    blog_images_dir = 'static/blog_images'
    analyze_png_files(blog_images_dir) 
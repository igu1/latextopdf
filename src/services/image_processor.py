"""
Image processing utilities for downloading and handling images
"""

import pathlib
import os
import re
import requests
import urllib.parse
import logging
import base64
import shutil

logger = logging.getLogger(__name__)


def extract_and_download_urls(latex_content: str, photo_dir: pathlib.Path) -> str:
    """
    Extract image URLs from LaTeX content and download them locally
    
    Args:
        latex_content: LaTeX content containing image references
        photo_dir: Directory to save downloaded images
        
    Returns:
        Processed LaTeX content with local image paths
    """
    url_pattern = r'\\includegraphics\[width=[^\]]*\]\{([^}]+)\}'
    
    def replace_url(match):
        original_path = match.group(1)
        
        if original_path.startswith('http://') or original_path.startswith('https://'):
            try:
                parsed_url = urllib.parse.urlparse(original_path)
                filename = os.path.basename(parsed_url.path)
                
                if not filename:
                    filename = f"downloaded_image_{hash(original_path)}.jpg"
                
                local_path = photo_dir / filename
                
                logger.info(f"Downloading image from URL: {original_path}")
                response = requests.get(original_path, timeout=10)
                response.raise_for_status()
                local_path.write_bytes(response.content)
                
                width_spec = match.group(0).split("[")[1].split("]")[0]
                
                return f'\\includegraphics[{width_spec}]{{./Photo/Qpbank/{filename}}}'
                
            except Exception as e:
                logger.warning(f"Failed to download {original_path}: {e}")
                return match.group(0)
        
        return match.group(0)
    
    processed_content = re.sub(url_pattern, replace_url, latex_content)
    return processed_content


def process_images(images: dict, photo_dir: pathlib.Path) -> None:
    """
    Process and save images from various sources (URLs, base64, local files)
    
    Args:
        images: Dictionary of image names and their data sources
        photo_dir: Directory to save processed images
    """
    if not images:
        return
        
    for img_name, img_data in images.items():
        img_path = photo_dir / img_name
        try:
            if img_data.startswith('http://') or img_data.startswith('https://'):
                logger.info(f"Downloading image from URL: {img_data}")
                response = requests.get(img_data, timeout=10)
                response.raise_for_status()
                img_path.write_bytes(response.content)
            elif img_data.startswith('data:image'):
                img_base64 = img_data.split(',', 1)[1]
                img_bytes = base64.b64decode(img_base64)
                img_path.write_bytes(img_bytes)
            elif os.path.isfile(img_data):
                shutil.copy(img_data, img_path)
            else:
                logger.warning(f"Image source not recognized for {img_name}: {img_data[:50]}...")
        except Exception as e:
            logger.warning(f"Could not process image {img_name}: {e}")

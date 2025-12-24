"""
Image processing utilities for downloading and handling images
"""

import pathlib
import os
import re
import asyncio
import logging
import base64
import shutil
import httpx
import urllib.parse

logger = logging.getLogger(__name__)


async def extract_and_download_urls(latex_content: str, photo_dir: pathlib.Path) -> str:
    """
    Extract image URLs from LaTeX content and download them locally
    
    Args:
        latex_content: LaTeX content containing image references
        photo_dir: Directory to save downloaded images
        
    Returns:
        Processed LaTeX content with local image paths
    """
    logger.info("Processing LaTeX content for image URLs")
    url_pattern = r'\\includegraphics\[width=[^\]]*\]\{([^}]+)\}'
    
    urls_to_download = []
    def find_urls(match):
        original_path = match.group(1)
        if original_path.startswith('http://') or original_path.startswith('https://'):
            urls_to_download.append(original_path)
        return match.group(0)
    
    re.sub(url_pattern, find_urls, latex_content)
    
    if urls_to_download:
        download_tasks = []
        for url in urls_to_download:
            download_tasks.append(_download_single_image(url, photo_dir))
        
        await asyncio.gather(*download_tasks, return_exceptions=True)
    
    def replace_with_local(match):
        original_path = match.group(1)
        
        if original_path.startswith('http://') or original_path.startswith('https://'):
            try:
                parsed_url = urllib.parse.urlparse(original_path)
                filename = os.path.basename(parsed_url.path)
                
                if not filename:
                    filename = f"downloaded_image_{hash(original_path)}.jpg"
                
                local_path = photo_dir / filename
                
                if local_path.exists():
                    width_spec = match.group(0).split("[")[1].split("]")[0]
                    return f'\\includegraphics[{width_spec}]{{./Photo/Qpbank/{filename}}}'
                else:
                    return match.group(0)
                    
            except Exception as e:
                logger.warning(f"Failed to process {original_path}: {e}")
                return match.group(0)
        
        return match.group(0)
    
    processed_content = re.sub(url_pattern, replace_with_local, latex_content)
    logger.info("Completed processing LaTeX content for image URLs")
    return processed_content


async def process_images(images: dict, photo_dir: pathlib.Path) -> None:
    """
    Process and save images from various sources (URLs, base64, local files)
    
    Args:
        images: Dictionary of image names and their data sources
        photo_dir: Directory to save processed images
    """
    if not images:
        logger.info("No images to process")
        return
        
    logger.info(f"Processing {len(images)} images")
    
    url_images = {}
    other_images = {}
    
    for img_name, img_data in images.items():
        if img_data.startswith('http://') or img_data.startswith('https://'):
            url_images[img_name] = img_data
        else:
            other_images[img_name] = img_data
    
    for img_name, img_data in other_images.items():
        img_path = photo_dir / img_name
        try:
            if img_data.startswith('data:image'):
                img_base64 = img_data.split(',', 1)[1]
                img_bytes = base64.b64decode(img_base64)
                img_path.write_bytes(img_bytes)
                logger.info(f"Processed base64 image: {img_name}")
            elif os.path.isfile(img_data):
                shutil.copy(img_data, img_path)
                logger.info(f"Copied local image: {img_name}")
            else:
                logger.warning(f"Image source not recognized for {img_name}: {img_data[:50]}...")
        except Exception as e:
            logger.warning(f"Could not process image {img_name}: {e}")
    
    if url_images:
        download_tasks = []
        for img_name, url in url_images.items():
            download_tasks.append(_download_image_with_name(img_name, url, photo_dir))
        
        await asyncio.gather(*download_tasks, return_exceptions=True)


async def _download_single_image(url: str, photo_dir: pathlib.Path) -> None:
    """
    Download a single image asynchronously
    
    Args:
        url: URL of the image to download
        photo_dir: Directory to save the image
    """
    try:
        parsed_url = urllib.parse.urlparse(url)
        filename = os.path.basename(parsed_url.path)
        
        if not filename:
            filename = f"downloaded_image_{hash(url)}.jpg"
        
        local_path = photo_dir / filename
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            local_path.write_bytes(response.content)
            
        logger.info(f"Successfully downloaded image: {filename}")
        
    except Exception as e:
        logger.warning(f"Failed to download {url}: {e}")


async def _download_image_with_name(img_name: str, url: str, photo_dir: pathlib.Path) -> None:
    """
    Download an image with a specific name asynchronously
    
    Args:
        img_name: Name to save the image as
        url: URL of the image to download
        photo_dir: Directory to save the image
    """
    img_path = photo_dir / img_name
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            img_path.write_bytes(response.content)
            
        logger.info(f"Successfully downloaded image: {img_name}")
        
    except Exception as e:
        logger.warning(f"Could not download image {img_name}: {e}")

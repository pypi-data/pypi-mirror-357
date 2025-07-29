import re
import logging
import httpx

async def extract_drive_direct_link(url):
    """
    Convert a Google Drive sharing link to a direct download link.
    Works with both file view links and sharing links.
    """
    logging.info(f"Converting URL to downloadable link: {url}")
    
    # If already a direct link, return it
    if not url or "drive.google.com" not in url:
        return url
    
    try:
        # Extract the file ID from various Google Drive URL formats
        file_id = None
        
        # Format: https://drive.google.com/file/d/FILE_ID/view
        file_pattern = r"drive\.google\.com/file/d/([^/]+)"
        file_match = re.search(file_pattern, url)
        if file_match:
            file_id = file_match.group(1)
        
        # Format: https://drive.google.com/open?id=FILE_ID
        open_pattern = r"drive\.google\.com/open\?id=([^&]+)"
        open_match = re.search(open_pattern, url)
        if not file_id and open_match:
            file_id = open_match.group(1)
            
        # Format: https://docs.google.com/document/d/FILE_ID/edit
        docs_pattern = r"docs\.google\.com/\w+/d/([^/]+)"
        docs_match = re.search(docs_pattern, url)
        if not file_id and docs_match:
            file_id = docs_match.group(1)
        
        if not file_id:
            logging.warning(f"Could not extract file ID from URL: {url}")
            return url
            
        # Create a direct download link
        direct_link = f"https://drive.google.com/uc?export=download&id={file_id}"
        
        # For files less than 100MB, we can use this direct link
        # For larger files, Google may present a confirmation page
        
        # Check if the file is available and get its size
        async with httpx.AsyncClient() as client:
            response = await client.head(direct_link, follow_redirects=True)
            
            content_type = response.headers.get("content-type", "")
            if "text/html" in content_type:
                # This might be a confirmation page for large files
                # Use the export=view URL instead which works better for media
                direct_link = f"https://drive.google.com/uc?export=view&id={file_id}"
        
        logging.info(f"Converted to downloadable link: {direct_link}")
        return direct_link
    
    except Exception as e:
        logging.error(f"Error converting Drive URL {url}: {str(e)}")
        # Return original URL if conversion fails
        return url
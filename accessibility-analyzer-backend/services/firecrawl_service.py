import asyncio
from firecrawl import AsyncFirecrawlApp
import os
import base64 # Add base64 import
import httpx  # Add httpx import
from dotenv import load_dotenv

load_dotenv()

async def scrape_website(url: str):
    """
    Asynchronously scrapes a website to get its HTML and a screenshot using the Firecrawl API.
    """
    api_key = os.getenv("FIRECRAWL_API_KEY")
    app = AsyncFirecrawlApp(api_key=api_key)

    try:
        # Scrape for both HTML and a standard screenshot
        response = await app.scrape_url(
            url=url,
            formats=['rawHtml', 'screenshot'] 
        )
        
        html_content = None
        screenshot_data_for_langchain = None # This should be base64

        # Try to get HTML content, prioritizing 'html', then 'rawHtml'
        if hasattr(response, 'html') and response.html:
            html_content = response.html
        elif hasattr(response, 'rawHtml') and response.rawHtml: # Check for rawHtml
            html_content = response.rawHtml
        elif hasattr(response, 'data') and isinstance(response.data, dict):
            html_content = response.data.get('html') or response.data.get('rawHtml')
        elif isinstance(response, dict): # If ScrapeResponse acts like a dict
            html_content = response.get('html') or response.get('rawHtml')

        # If html_content is a dict (e.g. from some nested structure), try to get 'content' or 'html' key
        if isinstance(html_content, dict):
            html_content = html_content.get('content', html_content.get('html', str(html_content)))
        
        if not html_content:
            print(f"DEV_NOTE: Could not extract HTML using 'html' or 'rawHtml' from Firecrawl ScrapeResponse. Object: {vars(response) if hasattr(response, '__dict__') else response}")

        screenshot_url = None
        if hasattr(response, 'screenshot') and response.screenshot:
            screenshot_url = response.screenshot
            if isinstance(screenshot_url, dict): # If response.screenshot is {'url': '...'}
                screenshot_url = screenshot_url.get('url', str(screenshot_url))
        elif hasattr(response, 'data') and isinstance(response.data, dict) and response.data.get('screenshot'):
            screenshot_url = response.data['screenshot']
            if isinstance(screenshot_url, dict):
                screenshot_url = screenshot_url.get('url', str(screenshot_url))
        elif isinstance(response, dict) and response.get('screenshot'): # If ScrapeResponse acts like a dict
            screenshot_url = response['screenshot']
            if isinstance(screenshot_url, dict):
                screenshot_url = screenshot_url.get('url', str(screenshot_url))
        else:
             print(f"DEV_NOTE: Could not extract screenshot URL from Firecrawl ScrapeResponse. Object: {vars(response) if hasattr(response, '__dict__') else response}")

        if html_content:
            print("DEV_NOTE: HTML content extracted successfully.")
        
        if screenshot_url:
            print(f"DEV_NOTE: Screenshot URL received: {screenshot_url}. Fetching and encoding to base64.")
            try:
                async with httpx.AsyncClient() as client:
                    img_response = await client.get(screenshot_url)
                    img_response.raise_for_status() # Raise an exception for bad status codes
                    screenshot_data_for_langchain = base64.b64encode(img_response.content).decode('utf-8')
                print("DEV_NOTE: Screenshot fetched and base64 encoded successfully.")
            except httpx.HTTPStatusError as http_err:
                print(f"HTTP error occurred while fetching screenshot: {http_err}")
                screenshot_data_for_langchain = None
            except Exception as fetch_err:
                print(f"An error occurred while fetching or encoding screenshot: {fetch_err}")
                screenshot_data_for_langchain = None
        else:
            print("DEV_NOTE: Screenshot URL not found in Firecrawl ScrapeResponse.")
            
        return {
            "html": html_content,
            "screenshot": screenshot_data_for_langchain
        }
    
    except Exception as e:
        print(f"An error occurred during scraping: {e}")
        return None

"""
Test script for MangoVoice scraper - processes only first page for testing.
"""

from scrape_mangovoice import MangoVoiceSeleniumScraper
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_single_page():
    """Test scraper with just the first page."""
    
    print("\n" + "="*60)
    print("TESTING SCRAPER - First Page Only")
    print("="*60)
    print("\nA browser window will open.")
    print("Please log in to MangoVoice when prompted.")
    print("The script will automatically continue after login.\n")
    print("="*60 + "\n")
    
    # Initialize scraper
    scraper = MangoVoiceSeleniumScraper(
        output_dir="./test_recordings",
        headless=False
    )
    
    # Run with max 1 page
    scraper.run(max_pages=1, output_csv="test_call_logs.csv")
    
    print("\n" + "="*60)
    print("Test complete! Check:")
    print("  - test_call_logs.csv (for scraped data)")
    print("  - ./test_recordings/ (for downloaded MP3s)")
    print("  - mangovoice_scraper.log (for execution log)")
    print("="*60 + "\n")


if __name__ == "__main__":
    test_single_page()

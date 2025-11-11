"""
MangoVoice Call Log Scraper - Selenium Version

This script uses Selenium to handle JavaScript and reCAPTCHA authentication,
scrapes call log data, downloads MP3 recordings, and exports to CSV.

Author: Generated for call log extraction
Date: 2025-10-02
"""

import os
import sys
import csv
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import logging
from typing import Dict, List, Optional
from pathlib import Path
import re
import stat

# Determine runtime base directory (script folder or bundled executable folder)
def get_runtime_base_dir() -> Path:
    """
    Return the directory containing the running script or PyInstaller executable.
    """
    if getattr(sys, "frozen", False):
        # Running from PyInstaller bundle
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


RUNTIME_BASE_DIR = get_runtime_base_dir()
LOG_FILE = RUNTIME_BASE_DIR / "mangovoice_scraper.log"


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class MangoVoiceSeleniumScraper:
    """Scraper for MangoVoice call logs using Selenium."""
    
    def __init__(self, output_dir: Optional[str] = None, headless: bool = False):
        """
        Initialize the scraper.
        
        Args:
            output_dir: Directory to save downloaded MP3 files
            headless: Run browser in headless mode (not recommended for login)
        """
        self.base_dir = RUNTIME_BASE_DIR

        if output_dir:
            output_path = Path(output_dir)
            if not output_path.is_absolute():
                output_path = (self.base_dir / output_path).resolve()
            self.output_dir = output_path
        else:
            self.output_dir = (self.base_dir / "call_recordings").resolve()

        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        logger.info(f"MP3 files will be saved to: {self.output_dir}")
        
        self.base_url = "https://admin.mangovoice.com"
        self.logs_url = f"{self.base_url}/super/account/logs/3417"
        self.driver = None
        self.headless = headless
        
        # CSV headers based on requirements
        self.csv_headers = [
            "Call Time", "Direction", "Source Number", "Source Name",
            "Source Ext", "Destination Number", "Destination Ext",
            "Duration", "Disposition", "Call Flow", "Time to Answer", "Call"
        ]
        
    def setup_driver(self):
        """Set up Chrome WebDriver with appropriate options."""
        logger.info("Setting up Chrome WebDriver...")
        
        options = webdriver.ChromeOptions()
        if self.headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Use webdriver-manager to automatically handle ChromeDriver
        raw_driver_path = ChromeDriverManager().install()
        driver_path = self._resolve_driver_binary(raw_driver_path)
        service = Service(str(driver_path))
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.maximize_window()
        
        logger.info("WebDriver ready!")

    def _resolve_driver_binary(self, raw_path: str) -> Path:
        """
        Normalize webdriver-manager output to the actual ChromeDriver executable.

        Args:
            raw_path: Path returned by webdriver-manager install()

        Returns:
            Absolute path to the ChromeDriver binary with execute permissions.
        """
        path = Path(raw_path).resolve()

        def _is_driver(candidate: Path) -> bool:
            return candidate.name in {"chromedriver", "chromedriver.exe"}

        if path.is_file() and _is_driver(path):
            if not os.access(path, os.X_OK):
                path.chmod(path.stat().st_mode | stat.S_IEXEC)
            return path

        search_dir = path.parent if path.suffix else path
        for candidate in sorted(search_dir.glob("chromedriver*")):
            if candidate.is_file() and _is_driver(candidate):
                if not os.access(candidate, os.X_OK):
                    candidate.chmod(candidate.stat().st_mode | stat.S_IEXEC)
                logger.debug(f"Resolved ChromeDriver executable at {candidate}")
                return candidate

        raise FileNotFoundError(
            f"ChromeDriver executable not found near webdriver-manager path: {raw_path}"
        )
    
    def wait_for_manual_login(self, timeout: int = 300):
        """
        Navigate to login page and wait for user to log in manually.
        
        Args:
            timeout: Maximum time to wait for login (seconds)
            
        Returns:
            True if login successful, False otherwise
        """
        logger.info("Navigating to MangoVoice login page...")
        logger.info("=" * 60)
        logger.info("MANUAL LOGIN REQUIRED")
        logger.info("=" * 60)
        logger.info("Please log in to MangoVoice in the browser window that opened.")
        logger.info(f"You have {timeout} seconds to complete the login.")
        logger.info("The script will automatically continue once you're logged in...")
        logger.info("=" * 60)
        
        try:
            # Navigate to the logs page (will redirect to login if not authenticated)
            self.driver.get(self.logs_url)
            
            # Wait for either the login form to disappear or the table to appear
            wait = WebDriverWait(self.driver, timeout)
            
            # Wait until we're no longer on the login page
            wait.until_not(
                EC.url_contains('/user/login')
            )
            
            # Give the page a moment to fully load
            time.sleep(3)
            
            # Check if we made it to the logs page
            if 'logs' in self.driver.current_url:
                logger.info("✓ Login successful!")
                return True
            else:
                logger.error("Login failed or timeout reached")
                return False
                
        except TimeoutException:
            logger.error(f"Login timeout after {timeout} seconds")
            return False
        except Exception as e:
            logger.error(f"Error during login wait: {e}")
            return False
    
    def wait_for_search_criteria(self):
        """
        Pause to allow user to apply filters/search criteria on the page.
        """
        logger.info("=" * 60)
        logger.info("APPLY SEARCH CRITERIA (OPTIONAL)")
        logger.info("=" * 60)
        logger.info("The browser is now on the Legacy Call Logs page.")
        logger.info("")
        logger.info("You can now:")
        logger.info("  • Set date range filters")
        logger.info("  • Search for specific phone numbers")
        logger.info("  • Apply any other search criteria")
        logger.info("  • Leave as-is to scrape all records")
        logger.info("")
        logger.info("=" * 60)
        logger.info("Press ENTER in this terminal when ready to start scraping...")
        logger.info("=" * 60)
        
        try:
            input()  # Wait for user to press Enter
            logger.info("✓ Starting scrape with current filters...")
            time.sleep(2)  # Brief pause to ensure any filters are applied
            return True
        except KeyboardInterrupt:
            logger.info("Scraping cancelled by user")
            return False
    
    def parse_table_row(self, row_element) -> Optional[Dict[str, str]]:
        """
        Parse a single table row element and extract call data.
        
        Args:
            row_element: Selenium WebElement for the row
            
        Returns:
            Dictionary of call data or None if parsing fails
        """
        try:
            cells = row_element.find_elements(By.TAG_NAME, 'td')
            if len(cells) < 11:
                return None
            
            call_data = {
                "Call Time": cells[0].text.strip(),
                "Direction": cells[1].text.strip(),
                "Source Number": cells[2].text.strip(),
                "Source Name": cells[3].text.strip(),
                "Source Ext": cells[4].text.strip(),
                "Destination Number": cells[5].text.strip(),
                "Destination Ext": cells[6].text.strip(),
                "Duration": cells[7].text.strip(),
                "Disposition": cells[8].text.strip(),
                "Call Flow": cells[9].text.strip().replace('\n', ' '),
                "Time to Answer": cells[10].text.strip(),
                "Call": ""
            }
            
            # Extract MP3 download link if present (column 12, index 11)
            mp3_link = None
            if len(cells) > 11:
                try:
                    link_element = cells[11].find_element(By.CLASS_NAME, 'callLogsDownload')
                    mp3_link = link_element.get_attribute('href')
                    if mp3_link:
                        call_data['_mp3_url'] = mp3_link
                except NoSuchElementException:
                    pass  # No download link for this row
            
            return call_data
            
        except Exception as e:
            logger.error(f"Error parsing row: {e}")
            return None
    
    def download_mp3(self, url: str, call_data: Dict[str, str]) -> Optional[str]:
        """
        Download MP3 file with retry logic and verification.
        
        Args:
            url: URL of the MP3 file
            call_data: Dictionary containing call information for filename generation
            
        Returns:
            Local filename if successful, None otherwise
        """
        # Generate a safe filename based on call data
        call_time = call_data.get("Call Time", "unknown")
        source = call_data.get("Source Number", "unknown")
        destination = call_data.get("Destination Number", "unknown")
        duration = call_data.get("Duration", "unknown")
        
        # Clean the filename components
        safe_time = re.sub(r'[^\w\-_]', '_', call_time)
        safe_source = re.sub(r'[^\w\-_]', '_', source)
        safe_dest = re.sub(r'[^\w\-_]', '_', destination)
        safe_duration = re.sub(r'[^\w\-_]', '_', duration)
        
        # Ensure output directory exists
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        # Create filename with duration included
        filename = f"{safe_time}_{safe_source}_to_{safe_dest}_{safe_duration}.mp3"
        filepath = self.output_dir / filename
        
        # Retry logic (3 attempts)
        for attempt in range(3):
            try:
                if attempt > 0:
                    logger.info(f"  Retry {attempt}/3: {filename}")
                else:
                    logger.info(f"Downloading: {filename}")
                
                # Get cookies from Selenium session
                selenium_cookies = self.driver.get_cookies()
                cookies = {cookie['name']: cookie['value'] for cookie in selenium_cookies}
                
                response = requests.get(url, cookies=cookies, stream=True, timeout=30)
                response.raise_for_status()
                
                # Check if we got actual content
                if 'content-length' in response.headers:
                    content_length = int(response.headers['content-length'])
                    if content_length < 100:  # MP3 should be larger than 100 bytes
                        logger.warning(f"  File too small ({content_length} bytes), may be invalid")
                
                # Save to disk
                bytes_written = 0
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:  # filter out keep-alive chunks
                            f.write(chunk)
                            bytes_written += len(chunk)
                
                # Verify file was actually written
                if filepath.exists() and filepath.stat().st_size > 0:
                    logger.info(f"  ✓ Downloaded: {filename} ({bytes_written} bytes)")
                    return filename
                else:
                    logger.error(f"  File created but empty: {filename}")
                    if attempt < 2:
                        time.sleep(1)  # Brief pause before retry
                        continue
                    return None
                    
            except requests.exceptions.Timeout:
                logger.warning(f"  Timeout downloading {filename} (attempt {attempt + 1}/3)")
                if attempt < 2:
                    time.sleep(2)
                    continue
            except requests.exceptions.RequestException as e:
                logger.error(f"  Request error downloading {filename}: {e}")
                if attempt < 2:
                    time.sleep(1)
                    continue
            except Exception as e:
                logger.error(f"  Unexpected error downloading {filename}: {e}")
                if attempt < 2:
                    time.sleep(1)
                    continue
        
        # All retries failed
        logger.error(f"  ✗ FAILED after 3 attempts: {filename}")
        return None
    
    def scrape_page(self, page_num: int = 1) -> tuple[List[Dict], bool]:
        """
        Scrape a single page of call logs.
        
        Args:
            page_num: Page number to scrape (for logging only)
            
        Returns:
            Tuple of (list of call data dicts, has_next_page boolean)
        """
        logger.info(f"Scraping page {page_num}...")
        
        try:
            # Wait for table to load (should already be loaded)
            wait = WebDriverWait(self.driver, 10)
            table = wait.until(
                EC.presence_of_element_located((By.ID, 'listLogs'))
            )
            
            # Get all rows from tbody
            tbody = table.find_element(By.TAG_NAME, 'tbody')
            rows = tbody.find_elements(By.TAG_NAME, 'tr')
            
            call_data_list = []
            for row_idx, row in enumerate(rows, 1):
                call_data = self.parse_table_row(row)
                if call_data:
                    # Download MP3 if link exists
                    if '_mp3_url' in call_data:
                        mp3_url = call_data.pop('_mp3_url')
                        filename = self.download_mp3(mp3_url, call_data)
                        if filename:
                            call_data['Call'] = filename
                        else:
                            logger.warning(f"  Row {row_idx}: Download failed, 'Call' column will be empty")
                    else:
                        logger.debug(f"  Row {row_idx}: No recording available")
                    
                    call_data_list.append(call_data)
            
            # Check if there's a next page button and if it's enabled
            has_next = False
            try:
                next_button = self.driver.find_element(By.LINK_TEXT, 'Next')
                # Check if it's enabled (not in a disabled parent)
                parent_classes = next_button.find_element(By.XPATH, '..').get_attribute('class')
                if 'disabled' not in parent_classes:
                    has_next = True
            except NoSuchElementException:
                pass
            
            logger.info(f"Scraped {len(call_data_list)} records from page {page_num}")
            
            return call_data_list, has_next
            
        except TimeoutException:
            logger.error(f"Timeout waiting for table on page {page_num}")
            return [], False
        except Exception as e:
            logger.error(f"Error scraping page {page_num}: {e}")
            return [], False
    
    def click_next_page(self) -> bool:
        """
        Click the 'Next' button to navigate to next page.
        This preserves search filters unlike loading a new URL.
        
        Returns:
            True if successfully navigated, False otherwise
        """
        try:
            wait = WebDriverWait(self.driver, 15)
            
            # Get the current first row's text before clicking (to detect change)
            table = self.driver.find_element(By.ID, 'listLogs')
            tbody = table.find_element(By.TAG_NAME, 'tbody')
            first_row = tbody.find_element(By.TAG_NAME, 'tr')
            old_first_row_text = first_row.text
            
            logger.info("Clicking 'Next' button to preserve search filters...")
            
            # Find the Next button
            next_button = self.driver.find_element(By.LINK_TEXT, 'Next')
            
            # Use JavaScript click to ensure it works even if obscured
            self.driver.execute_script("arguments[0].click();", next_button)
            
            # Wait for the table content to change (DataTables updates via AJAX)
            # We wait for the first row text to be different
            def first_row_changed(driver):
                try:
                    new_tbody = driver.find_element(By.ID, 'listLogs').find_element(By.TAG_NAME, 'tbody')
                    new_first_row = new_tbody.find_element(By.TAG_NAME, 'tr')
                    return new_first_row.text != old_first_row_text
                except:
                    return False
            
            wait.until(first_row_changed)
            
            # Brief pause for page to fully render
            time.sleep(1)
            
            logger.info("✓ Successfully navigated to next page")
            return True
            
        except TimeoutException:
            logger.error("Timeout waiting for next page to load (table content didn't change)")
            return False
        except NoSuchElementException as e:
            logger.error(f"Could not find Next button or table: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error navigating to next page: {e}")
            return False
    
    def scrape_all_pages(self, max_pages: Optional[int] = None) -> List[Dict]:
        """
        Scrape all pages of call logs.
        
        This method clicks the 'Next' button to navigate between pages,
        which preserves any search filters applied by the user.
        
        Args:
            max_pages: Maximum number of pages to scrape (None for all)
            
        Returns:
            List of all call data dictionaries
        """
        all_data = []
        page_num = 1
        has_next = True
        
        while has_next:
            if max_pages and page_num > max_pages:
                logger.info(f"Reached maximum page limit: {max_pages}")
                break
            
            # Scrape current page
            page_data, has_next = self.scrape_page(page_num)
            
            # Add data to our collection (even if navigation fails later)
            all_data.extend(page_data)
            
            # If there's a next page, navigate to it
            if has_next:
                if not self.click_next_page():
                    logger.warning("Failed to navigate to next page, stopping pagination")
                    break
            
            page_num += 1
        
        logger.info(f"Total records scraped: {len(all_data)}")
        return all_data
    
    def export_to_csv(self, data: List[Dict], output_file: Optional[str] = None):
        """
        Export scraped data to CSV file and show download summary.
        
        Args:
            data: List of call data dictionaries
            output_file: Output CSV filename or path
        """
        if output_file:
            output_path = Path(output_file)
            if not output_path.is_absolute():
                output_path = (self.base_dir / output_path).resolve()
        else:
            output_path = self.base_dir / "mangovoice_call_logs.csv"

        logger.info(f"Exporting data to {output_path}...")
        
        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=self.csv_headers)
                writer.writeheader()
                writer.writerows(data)
            
            logger.info(f"Successfully exported {len(data)} records to {output_path}")
            
            # Show download summary
            total_calls = len(data)
            downloaded = sum(1 for record in data if record.get('Call'))
            failed = total_calls - downloaded
            
            logger.info("=" * 60)
            logger.info("DOWNLOAD SUMMARY")
            logger.info("=" * 60)
            logger.info(f"Total call records: {total_calls}")
            logger.info(f"Successfully downloaded: {downloaded}")
            if failed > 0:
                logger.warning(f"Failed/Missing downloads: {failed}")
                logger.info("Check the log above for '✗ FAILED' messages to see which files failed")
            else:
                logger.info(f"✓ All MP3 files downloaded successfully!")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
    
    def run(self, max_pages: Optional[int] = None, output_csv: str = "call_logs.csv", 
            allow_search_criteria: bool = True):
        """
        Main execution method.
        
        Args:
            max_pages: Maximum number of pages to scrape (None for all)
            output_csv: Output CSV filename
            allow_search_criteria: If True, pause for user to apply search filters
        """
        logger.info("Starting MangoVoice scraper with Selenium...")
        
        try:
            # Step 1: Setup WebDriver
            self.setup_driver()
            
            # Step 2: Wait for manual login
            if not self.wait_for_manual_login():
                logger.error("Failed to login. Exiting.")
                return
            
            # Step 3: Allow user to apply search criteria
            if allow_search_criteria:
                if not self.wait_for_search_criteria():
                    logger.info("Scraping cancelled. Exiting.")
                    return
            
            # Step 4: Scrape all pages
            logger.info(f"Scraping Legacy Call Logs from: {self.logs_url}")
            all_data = self.scrape_all_pages(max_pages=max_pages)
            
            if not all_data:
                logger.warning("No data scraped. Exiting.")
                return
            
            # Step 5: Export to CSV
            self.export_to_csv(all_data, output_csv)
            
            logger.info("Scraping completed successfully!")
            
        finally:
            # Always close the browser
            if self.driver:
                logger.info("Closing browser...")
                self.driver.quit()


def main():
    """Main entry point."""
    # Initialize scraper
    scraper = MangoVoiceSeleniumScraper(
        output_dir="./call_recordings",
        headless=False  # Keep browser visible for manual login
    )
    
    # Run the scraper
    # Set max_pages=1 for testing, None for all pages
    # Set allow_search_criteria=True to pause for filters
    scraper.run(
        max_pages=None, 
        output_csv="mangovoice_call_logs.csv",
        allow_search_criteria=True
    )


if __name__ == "__main__":
    main()

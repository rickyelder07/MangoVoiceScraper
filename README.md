# MangoVoice Call Log Scraper

A Python script to extract call logs and download audio recordings from MangoVoice admin portal.

## Features

- 🌐 Uses Selenium WebDriver to handle JavaScript and reCAPTCHA
- 🔐 Manual login support (you log in through the browser)
- 📊 Extracts all call log data to CSV from Legacy Call Logs
- 🎵 Downloads MP3 recordings automatically
- 📄 Handles pagination (processes all 10,000+ records)
- 🛡️ Robust error handling and logging
- ⏸️ Rate limiting to be respectful to servers
- 📝 Detailed logging to file and console

## Prerequisites

- Python 3.8 or higher
- Chrome browser installed
- MangoVoice admin account credentials

## Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   
   This will install:
   - `selenium` - For browser automation
   - `beautifulsoup4` - For HTML parsing
   - `webdriver-manager` - Automatically manages ChromeDriver
   
2. **No credential configuration needed!**
   - The script uses manual login through the browser
   - You'll log in normally when the browser window opens

## Usage

### Basic Usage

1. **Run the script:**
   ```bash
   python scrape_mangovoice.py
   ```

2. **A Chrome browser window will open automatically**

3. **Log in to MangoVoice** when the browser opens
   - Enter your email and password
   - Complete the reCAPTCHA if prompted
   - The script waits up to 5 minutes for you to log in

4. **Apply search criteria** (optional)
   - After login, browser shows Legacy Call Logs page
   - Apply any filters you want:
     - Date range (e.g., last 30 days)
     - Search by phone number
     - Filter by call direction (Inbound/Outbound)
   - Press **ENTER in the terminal** when ready

5. **Script automatically continues** scraping
   - Scrapes all pages (with your filters applied)
   - Downloads MP3 files
   - Exports to CSV

### Testing (Limited Pages)

To test with just the first page:

```bash
python test_scraper.py
```

This will:
- Open Chrome browser
- Wait for you to log in
- Scrape only the first page (25 entries)
- Save to `test_call_logs.csv` and `./test_recordings/`

### Advanced Usage

You can also import and use the scraper as a module:

```python
from scrape_mangovoice import MangoVoiceSeleniumScraper

scraper = MangoVoiceSeleniumScraper(
    output_dir="./my_recordings",
    headless=False  # Set to True to hide browser (not recommended for login)
)

# Scrape first 5 pages only, with filter pause
scraper.run(
    max_pages=5, 
    output_csv="call_logs_sample.csv",
    allow_search_criteria=True  # Set to False to skip filter pause
)
```

## Output

The script generates:

1. **CSV File** (`mangovoice_call_logs.csv`):
   - Call Time
   - Direction (Inbound/Outbound)
   - Source Number
   - Source Name
   - Source Ext
   - Destination Number
   - Destination Ext
   - Duration
   - Disposition
   - Call Flow
   - Time to Answer
   - Call (filename of downloaded MP3)

2. **MP3 Files** (`./call_recordings/`):
   - Saved next to the script or bundled executable that launched the scraper
   - Named as: `{call_time}_{source}_{destination}.mp3`
   - Only downloaded if available for that call

3. **Log File** (`mangovoice_scraper.log`):
   - Created alongside the script/binary
   - Detailed execution log

## Configuration

### Custom Output Directory

```python
scraper = MangoVoiceSeleniumScraper(
    output_dir="./my_custom_folder"  # Change this
)
```

### Rate Limiting

The script includes a 2-second delay between page requests. Adjust in `scrape_all_pages()`:

```python
time.sleep(2)  # Modify this value if needed
```

## Error Handling

The script handles:
- Missing data in table cells
- Missing MP3 files (rows without recordings)
- Network errors and timeouts
- Authentication failures
- Pagination edge cases

All errors are logged to both console and `mangovoice_scraper.log`.

## Security Notes

⚠️ **IMPORTANT:**
- Login is done manually through the browser - your credentials are never stored
- The script uses your browser session for authenticated requests
- Downloaded MP3s and CSV files contain call data - handle appropriately
- The `.gitignore` file protects sensitive data files

## Packaged Builds

Executable distributions for macOS and Windows can be produced with PyInstaller.
Follow the detailed steps in `docs/pyinstaller-builds.md` for dependency audit,
build commands, signing guidance, and post-build verification.

## Troubleshooting

### Browser Doesn't Open
- Make sure Chrome browser is installed
- Check if ChromeDriver is being downloaded properly
- Try running with `sudo` on Mac/Linux if permissions issue

### Login Timeout
- You have 5 minutes to complete login
- Make sure to complete the reCAPTCHA
- Click through to the logs page if not automatically redirected

### No Data Scraped
- Check if HTML structure has changed (view page source)
- Verify table class names match
- Check browser developer tools for actual table structure

### Download Failures
- Verify network connectivity
- Check if MP3 URLs are accessible
- Increase timeout values if on slow connection

## Project Structure

```
audiocode/
├── scrape_mangovoice.py    # Main scraper script
├── requirements.txt         # Python dependencies
├── .env.example            # Example environment file
├── .gitignore              # Git ignore rules
├── README.md               # This file
├── call_recordings/        # Downloaded MP3s (generated)
├── mangovoice_call_logs.csv  # Output CSV (generated)
└── mangovoice_scraper.log    # Execution log (generated)
```

## License

This script is for authorized use only. Ensure you have permission to scrape and download data from MangoVoice.


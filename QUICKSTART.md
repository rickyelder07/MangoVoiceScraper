# 🚀 Quick Start Guide - Selenium Version

## What Changed?

The scraper now uses **Selenium WebDriver** instead of the `requests` library because MangoVoice uses:
- Google reCAPTCHA v3 for login protection
- JavaScript to load the call logs table

## How It Works Now

1. **Script opens Chrome browser** automatically
2. **You log in manually** (handles reCAPTCHA easily)
3. **Script takes over** and scrapes all data
4. **Downloads complete** - get your CSV + MP3s

---

## 🎯 Run Your First Test

```bash
python3 test_scraper.py
```

### What to Expect:

1. ✅ Chrome browser opens automatically
2. ✅ You'll see the MangoVoice login page
3. ✅ **Log in with your credentials** (ehren@solakidsdental.com)
4. ✅ Complete reCAPTCHA if prompted
5. ✅ Script detects successful login
6. ✅ Browser navigates to Legacy Call Logs
7. ✅ Script scrapes first page (25 entries)
8. ✅ Downloads MP3 files to `./test_recordings/`
9. ✅ Creates `test_call_logs.csv`
10. ✅ Browser closes automatically

**Time: 2-3 minutes total**

---

## 📊 Run Full Scraper (All 10,734+ Entries)

After testing works:

```bash
python3 scrape_mangovoice.py
```

**Estimated time:** 30-45 minutes for all pages
- Processes ~25 entries per page
- 2-second delay between pages
- Downloads MP3s as it goes

---

## 📁 Output Files

After running:

```
audiocode/
├── call_recordings/          # All MP3 files
│   ├── October_2nd_2025_12_35_pm_+1__323__325_5641_to__213__631_0889.mp3
│   ├── October_2nd_2025_12_30_pm_+1__323__325_5641_to__323__944_8455.mp3
│   └── ... (thousands more)
├── mangovoice_call_logs.csv  # All call data
└── mangovoice_scraper.log    # Execution log
```

---

## 💡 Tips

### Speed Up Testing
- Use `test_scraper.py` first (1 page only)
- Check CSV and MP3s look correct
- Then run full scraper

### Troubleshooting
- **Browser doesn't open?** → Make sure Chrome is installed
- **Login timeout?** → You have 5 minutes to log in
- **Table not found?** → Make sure you reach the Legacy Call Logs page

### Stop & Resume
- Press `Ctrl+C` to stop the script
- Currently no resume feature (would need to add page tracking)
- Recommended: Run overnight for full scrape

---

## 🎉 That's It!

The Selenium version is more reliable and handles:
- ✅ reCAPTCHA automatically (you do it once)
- ✅ JavaScript-loaded content
- ✅ Complex authentication flows
- ✅ Same great CSV + MP3 output

**Ready to try?** Run `python3 test_scraper.py` now! 🚀


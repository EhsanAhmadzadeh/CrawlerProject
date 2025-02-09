# 🕵️‍♂️ Web Scraper for App Metadata & Comments

This project is an **asynchronous web scraper** built with **httpx, lxml, and Playwright** to extract app metadata and user comments from CafeBazaar.

## 🚀 Features

- ✅ **Async HTTP Requests** (`httpx`) for fast page fetching
- ✅ **JavaScript-rendered pages** (`playwright`) for handling dynamic content
- ✅ **Parallel execution** (`asyncio.gather`) for efficiency
- ✅ **Data extraction** (`BeautifulSoup + lxml`)
- ✅ **Automatic data storage** (`pandas` → Excel)
- ✅ **Logging & error handling** with retry logic

---

## 📦 Installation

### 1️⃣ Clone this repository

```bash
git clone https://github.com/yourusername/app-scraper.git
cd app-scraper
```

### 2️⃣ Create a virtual environment (optional but recommended)

```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Install Playwright Browsers

Playwright needs Chromium to run:

```bash
playwright install
```

---

## ⚙️ Configuration

The scraper configuration is managed in `config.py`, allowing customization of key parameters such as timeouts, URLs, logging, and storage paths. Below are the main configurations available:

- **MAIN_DOMAIN**: The base URL of CafeBazaar.
- **APP_ROUTE**: The specific page route to extract apps from.
- **FETCH_METADATA_TIMEOUT**: Timeout (in seconds) for fetching app metadata.
- **FETCH_COMMENTS_TIMEOUT**: Timeout (in seconds) for fetching comments.
- **FETCH_APP_LINKS_TIMEOUT**: Timeout for retrieving app links.
- **HEADLESS_MODE**: Determines if Playwright should run in headless mode.
- **LOG_FILE**: Path to store logs.
- **EXCEL_FILE**: Path to store extracted app data in an Excel file.
- **SHOW_TRACEBACKS**: Toggle for displaying detailed error logs.
- **FAILED_TASKS_FILE**: Path for storing failed scraping tasks.
- **LOG_LEVEL**: Defines the verbosity of logging (e.g., DEBUG, INFO, WARNING, ERROR).
- **LOG_MORE_COMMENTS_BUTTON_CLICKED**: Boolean to log each 'Load More Comments' click.
- **REFRESH_NO_COMMENTS_PAGE_TIMEOUT**: Timeout (in ms) for initially loading a page with no comments.
- **REFRESH_ALL_COMMENTS_PAGE_TIMEOUT**: Timeout (in seconds) for fetching all comments.
- **MAX_RETRIES**: Maximum number of retry attempts for failed HTTP requests.
- **REQUEST_TIMEOUT**: Default timeout (in seconds) for HTTP requests.
- **FETCH_WITH_TIMEOUT**: Boolean flag to enable/disable fetching with a timeout constraint.

---

## ▶️ Running the Scraper

Simply execute:

```bash
python run.py
```

This will:

1. Extract app links from CafeBazaar.
2. Fetch **app metadata** (name, description, images, rating, etc.).
3. Extract **user comments** using **Playwright**.
4. Save everything to an Excel file.

---

## 📜 Respect for Robots.txt & Legal Disclaimer

This scraper is for **showcasing skills** and adheres to website guidelines by respecting the following `robots.txt` rules:

```
User-agent: *

Disallow: /download/*
Disallow: /json/*
Disallow: /api/*
Disallow: /s?q=*
Disallow: /login
Disallow: /video*
Disallow: /signin?*

Allow: /signin?l=en
```

---

## 📞 Contact Information

If you have any question about the project, feel free to reach out:

📧 Email: ehsansolout@gmail.com  
📞 Phone: 09222312735

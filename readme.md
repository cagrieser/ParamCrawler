# Recursive Parameter & Keyword Crawler 🕷️

**Recursive Parameter & Keyword Crawler** is a specialized reconnaissance tool designed for penetration testers, bug bounty hunters, and security researchers.

This Python script recursively crawls a target website to discover hidden parameters, endpoints, and significant keywords by analyzing **HTML forms**, **URL query strings**, **JavaScript variables**, and **URL paths**.

The primary goal is to generate highly specific, target-tailored wordlists for use in fuzzing (e.g., with `ffuf`, `gobuster`, `burp intruder`) or parameter analysis.

## 🚀 Features

* **Recursive Crawling:** Starts from a base URL and navigates through internal links up to a specified depth.
* **Smart Parameter Extraction:** Identifies potential parameters from:
    * **URL Query Strings:** (e.g., `?id=123` -> extracts `id`)
    * **HTML Forms:** (`<input name="user">`, `<select id="lang">`)
* **JavaScript Analysis:** Parses inline scripts and external `.js` files to extract variable names and object properties. It features a built-in "Noise Filter" to remove common JavaScript reserved keywords (like `var`, `function`, `document`), keeping only unique, developer-defined terms.
* **Path Segmentation:** Breaks down URL paths to find hidden endpoints (e.g., `/api/v2/login` -> extracts `api`, `v2`, `login`).
* **WAF/Bot Bypass:** Utilizes `cloudscraper` to handle basic anti-bot protections and Cloudflare challenges.
* **Clean Output:** Generates deduplicated, sorted wordlists named dynamically based on the target domain.

## 📦 Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/cagrieser/ParamCrawler.git](https://github.com/cagrieser/ParamCrawler.git)
    cd ParamCrawler
    ```

2.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## 🛠️ Usage

The basic syntax is straightforward:

```bash
python3 ParamCrawler.py -u <target_url> [-d <depth>]
```
# Q1 - mdcomputers.in Product Scraper

## Overview

This program searches for products on mdcomputers.in using a search term provided by the user. It extracts the product details from the search results and displays them in a readable format. The output can also be saved as CSV or JSON.

### Example

```bash
pip install requests beautifulsoup4

python scrape_mdcomputers.py "external hard drive"

python scrape_mdcomputers.py "external hard drive" --pages 3 --format csv -o results.csv
```

## Search URL

The scraper uses the same search URL format used by the website:

```
https://mdcomputers.in/?route=product/search&search=<search_term>
```

If multiple pages are requested, the page number is added using the `page` parameter.

## Approach

### Libraries Used

- **requests** – to download the search results page.
- **BeautifulSoup** – to parse the HTML and extract product details.

I used these libraries because the required information is available in the page source, so a browser automation tool like Selenium is not necessary.

### Parsing

The scraper first looks for the expected product layout used on the website and extracts:

- Product name
- Product URL
- Current price
- Original price (if available)
- Discount percentage (if available)

If the expected HTML structure is not found, it uses a fallback method that searches product links directly and tries to extract the nearby price information. This makes the scraper more tolerant to small HTML changes.

## Output

The program supports three output formats:

- Table (default)
- CSV
- JSON

This makes it easy to either read the results directly or use them in another application.

## Error Handling

The scraper includes basic error handling for:

- Network errors
- Request timeout
- Empty search results

## Notes

I could not test the scraper directly against the live website from my current environment because external access to the site was restricted. To verify the parsing logic, I created a sample HTML file (`test_sample.html`) based on the page structure and tested the parser against it.
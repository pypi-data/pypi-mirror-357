from gsearchpy import GoogleScraper


def main():
    print("[+] Starting cookie creation...")
    query = "best VSCode extensions for productivity"
    scraper = GoogleScraper()
    html = scraper.google_search(query)

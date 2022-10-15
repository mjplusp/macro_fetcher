from crawler import MacroFetcher

print("Crawler Started")

crawler = MacroFetcher()
crawler.sign_in()

if crawler.is_signed_in:
    crawler.fetch_infinitely()
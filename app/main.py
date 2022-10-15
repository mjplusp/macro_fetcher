import sys
from crawler import MacroFetcher

print("Crawler Started")

driver_path = "chromedriver"
if len(sys.argv) > 1:
    driver_path = sys.argv[1]

print("driver path: ", driver_path)

crawler = MacroFetcher(driver_path=driver_path)
crawler.sign_in()

if crawler.is_signed_in:
    crawler.fetch_infinitely()
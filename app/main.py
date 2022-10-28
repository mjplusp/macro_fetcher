import sys
from crawler import MacroFetcher
import schedule
import time

# # Run job every 3 second/minute/hour/day/week,
# # Starting 3 second/minute/hour/day/week from now
# schedule.every(3).seconds.do(job)
# schedule.every(3).minutes.do(job)
# schedule.every(3).hours.do(job)
# schedule.every(3).days.do(job)
# schedule.every(3).weeks.do(job)

# # Run job every minute at the 23rd second
# schedule.every().minute.at(":23").do(job)

driver_path = "chromedriver"
if len(sys.argv) > 1:
    driver_path = sys.argv[1]

print("Crawler Started. Driver Path: ", driver_path)
crawler = MacroFetcher(driver_path=driver_path, headless=True)
print("Signing In ...")
crawler.sign_in()

if crawler.is_signed_in:
    crawler.enter_watchlist()
    # crawler.fetch_data()
    schedule.every(10).seconds.do(crawler.fetch_data)
    schedule.every().minute.at(":00").do(crawler.enter_watchlist)

    while True:
        schedule.run_pending()
        time.sleep(1)

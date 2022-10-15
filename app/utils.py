from datetime import datetime
from typing import Tuple
import pytz

def get_day_and_time() -> Tuple[str, str]:
    local_tz = pytz.timezone('Asia/Seoul')
    utc_now = datetime.now()

    kst_now_string = utc_now.astimezone(local_tz).strftime("%Y%m%d-%H%M%S")

    dayandtime = kst_now_string.split("-")

    return (dayandtime[0], dayandtime[1])

if __name__ == "__main__":
    print(get_day_and_time())
from datetime import datetime
import time
from dotenv import load_dotenv

from config import CITY_DISTRICTS, RENT_RANGE, MIN_PING, MAX_PING, KINDS, NEW_WITHIN_HOURS
from app.line_notify import push_to_line
from app.libs.utils import get_driver, get_page_content

load_dotenv()

def generate_urls():
    urls = []
    base = "https://rent.591.com.tw/list?region={region}&section={section}&kind={kind}&price={min_rent}$_{max_rent}$&acreage={min_area}$_{max_area}$&other=newPost&sort=posttime_desc"
    for region, sections in CITY_DISTRICTS.items():
        section = ",".join(sections)
        for kind in KINDS:
            url = base.format(
                kind=kind,
                region=region,
                section=section,
                min_rent=RENT_RANGE[0],
                max_rent=RENT_RANGE[1],
                min_area=MIN_PING,
                max_area=MAX_PING
            )
            urls.append(url)
    return urls

def is_new_listing(time_text):
    now = datetime.now()
    if "分鐘" in time_text:
        return True
    if "小時" in time_text:
        hour = int(time_text.split("小時")[0])
        return hour <= NEW_WITHIN_HOURS
    return False

def run_crawler():
    driver = get_driver()
    urls = generate_urls()
    print(f"[Crawler] Start crawling {len(urls)} URLs")

    for url in urls:
        soup = get_page_content(driver, url)
        get_recommends(soup)
        get_normal(soup, url, driver)



    driver.quit()
    print("[Crawler] Done.")

def get_recommends(soup):
    listings = soup.select("div.recommend-ware")
    data = []
    for item in listings:
        try:
            title = item.select_one("a.title").text.strip()
            price = item.select_one("div.price-info").text.strip() + "元"
            area = item.select_one("span.area").text.strip()
            link = item.select_one('a.title')['href']

            print("Title:", title)
            print("Price:", price)
            print("Area:", area)
            print("Link:", link)
            print("-" * 20)

            #push_to_line(f"{title}\n租金：{price}\n坪數：{area}\n{link}")
            data.append(f"{title}\n租金：{price}\n坪數：{area}\n{link}")
        except Exception as e:
            print("[Error] Failed to parse listing:", e)
    push_to_line("推薦物件：\n" + "\n".join(data))

def get_normal(soup, url, driver):
    page = 1
    data = []
    while soup.select_one('.empty') is None:
        print(f'getting page {page}')
        data.append(get_normal_items(soup))
        print(f'successfully crawl page: {page}')
        page += 1
        soup = get_page_content(driver, url + f'&page={page}')
        time.sleep(1)
    push_to_line("一般物件：\n" + "\n".join(data))

def get_normal_items(soup):
    listings = soup.select('.item')
    data = []
    for item in listings:
        try:
            # Title and Link
            title_element = item.select_one(".item-info-title a.link.v-middle")
            title = title_element.text.strip() if title_element else None
            link = title_element['href'] if title_element and 'href' in title_element.attrs else None

            # Time
            time_element = item.select("div.item-info-txt.role-name span.line")
            time = time_element[0].text.strip() if len(time_element) > 0 else None
            if time_element and not is_new_listing(time):
                continue

            print("Title:", title)
            print("Link:", link)
            print("Time:", time)
            print("-" * 20)

            data.append(f"{title}\n{link}")
            #push_to_line(f"{title}\n{link}")
        except Exception as e:
            print("[Error] Failed to parse listing:", e)

    return '\n'.join(data)
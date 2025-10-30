from datetime import datetime
import time
import sys
import traceback
from dotenv import load_dotenv

from config import CITY_DISTRICTS, RENT_RANGE, MIN_PING, MAX_PING, KINDS, NEW_WITHIN_HOURS, GET_RECOMMENDS, GET_NORMAL, NOT_COVER, ALL_SEX, BOY_ONLY, SEARCH_MODE, METRO_STATIONS
from app.line_notify import push_to_line
from app.libs.utils import get_driver, get_page_content

load_dotenv()

def generate_urls():
    """
    Generate a list of URLs to scrape based on the configuration.
    """
    urls = []

    # 根據模式決定使用的基底設定
    config = {
        "metro": {
            "base": "https://rent.591.com.tw/list?metro={main}&station={sub}&kind={kind}",
            "data": METRO_STATIONS,
            "key_name": "metro"
        },
        "district": {
            "base": "https://rent.591.com.tw/list?region={main}&section={sub}&kind={kind}",
            "data": CITY_DISTRICTS,
            "key_name": "region"
        }
    }

    # 根據模式取出設定
    mode_conf = config.get(SEARCH_MODE)
    if not mode_conf:
        raise ValueError(f"Invalid SEARCH_MODE: {SEARCH_MODE}")

    # 預先組好共通查詢參數
    common_params = f"&price={RENT_RANGE[0]}$_{RENT_RANGE[1]}$&acreage={MIN_PING}$_{MAX_PING}$&other=cook,newPost&sort=posttime_desc&option=washer"

    # notice 組合
    notice_flags = [
        flag for flag, enabled in [
            ("not_cover", NOT_COVER),
            ("all_sex", ALL_SEX),
            ("boy", BOY_ONLY)
        ] if enabled
    ]
    notice_param = f"&notice={','.join(notice_flags)}" if notice_flags else ""

    # 生成 URL
    for main, subs in mode_conf["data"].items():
        sub_param = ",".join(subs)
        for kind in KINDS:
            url = mode_conf["base"].format(main=main, sub=sub_param, kind=kind)
            urls.append(url + common_params + notice_param)

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
    try:
        driver = get_driver()
        urls = generate_urls()
        items = {}
        
        print(f"[Crawler] Start crawling {len(urls)} URLs")

        for url in urls:
            try:
                soup = get_page_content(driver, url)
                if soup:
                    if GET_RECOMMENDS:
                        recommends = get_recommends(soup)
                        if recommends:
                            items.update(recommends)
                    if GET_NORMAL:
                        normal_items = get_normal(soup, url, driver)
                        if normal_items:
                            items.update(normal_items)
                else:
                    print(f"[Error] Failed to get content for URL: {url}")
            except Exception as e:
                error_msg = f"[Error] Failed to process URL {url}: {str(e)}"
                print(error_msg)
                traceback.print_exc()
                continue  # Continue with next URL even if this one fails

        driver.quit()
        print("[Crawler] Done.")
        return items
    except Exception as e:
        error_msg = f"[Critical Error] Crawler failed: {str(e)}"
        print(error_msg)
        traceback.print_exc()
        return None

def get_recommends(soup):
    if not soup:
        print("[Error] Empty soup object in get_recommends")
        return None
        
    listings = soup.select("div.recommend-ware")
    if not listings:
        print("[Info] No recommended listings found")
        return None
        
    data = {}
    for item in listings:
        try:
            title_elem = item.select_one("a.title")
            price_elem = item.select_one("div.price-info")
            area_elem = item.select_one("span.area")
            
            if not all([title_elem, price_elem, area_elem]):
                print("[Warning] Missing elements in listing")
                continue
                
            title = title_elem.text.strip()
            price = price_elem.text.strip() + "元"
            area = area_elem.text.strip()
            link = title_elem['href'] if 'href' in title_elem.attrs else None
            id = link.split("/")[-1] if link else None

            if not link:
                print("[Warning] Missing link in listing")
                continue
            
            print("ID:", id)
            print("Title:", title)
            print("Price:", price)
            print("Area:", area)
            print("Link:", link)
            print("-" * 20)

            data[id] = f"ID: {id}\n{title}\n租金：{price}\n坪數：{area}\n{link}\n"
        except Exception as e:
            print(f"[Error] Failed to parse listing: {str(e)}")
            traceback.print_exc()
            continue

    if data:
        try:
            return data
        except Exception as e:
            print(f"[Error] Failed to return data: {str(e)}")
            traceback.print_exc()
            return None
    else:
        print("[Info] No valid recommended listings found")
        return None

def get_normal(soup, url, driver):
    if not soup:
        print("[Error] Empty soup object in get_normal")
        return
        
    page = 1
    data = {}
    max_pages = 5  # Safety limit to prevent infinite loops
    
    try:
        while soup.select_one('.empty') is None and page <= max_pages:
            print(f'Getting page {page}')
            items_data = get_normal_items(soup)
            if items_data:
                data.update(items_data)
                print(f'Successfully crawled page: {page}')
            else:
                print(f'No items found on page {page}')
                
            page += 1
            try:
                next_url = url + f'&page={page}'
                soup = get_page_content(driver, next_url)
                if not soup:
                    print(f"[Error] Failed to get content for URL: {next_url}")
                    break
                time.sleep(1)
            except Exception as e:
                print(f"[Error] Failed to fetch page {page}: {str(e)}")
                traceback.print_exc()
                break
    except Exception as e:
        print(f"[Error] Error in pagination: {str(e)}")
        traceback.print_exc()
    
    if data:
        try:
            return data
        except Exception as e:
            print(f"[Error] Failed to send Line notification: {str(e)}")
            traceback.print_exc()
            return None
    else:
        print("[Info] No valid normal listings to send")
        return None

def get_normal_items(soup):
    if not soup:
        print("[Error] Empty soup object in get_normal_items")
        return None
        
    listings = soup.select('.item')
    if not listings:
        print("[Info] No normal listings found")
        return None
        
    data = {}
    for item in listings:
        try:
            # Title and Link
            title_element = item.select_one(".item-info-title a.link.v-middle")
            if not title_element:
                print("[Warning] Missing title element in listing")
                continue
                
            title = title_element.text.strip() if title_element else None
            link = title_element['href'] if title_element and 'href' in title_element.attrs else None
            
            if not title or not link:
                print("[Warning] Missing title or link in listing")
                continue

            # Time
            time_element = item.select("div.item-info-txt.role-name span.line")
            time = time_element[0].text.strip() if len(time_element) > 0 else None
            
            if not time:
                print("[Warning] Missing time information in listing")
                continue
                
            if not is_new_listing(time):
                continue
            
            id = link.split("/")[-1] if link else None
            print("ID:", id)
            print("Title:", title)
            print("Link:", link)
            print("Time:", time)
            print("-" * 20)

            data[id] = f"ID: {id}\n{title}\n{link}\n"
        except IndexError as e:
            print(f"[Error] Index error while parsing listing: {str(e)}")
            continue
        except Exception as e:
            print(f"[Error] Failed to parse listing: {str(e)}")
            traceback.print_exc()
            continue

    if data:
        return data
    else:
        return None

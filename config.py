SEARCH_MODE = "metro"  # "district" or "metro"

CITY_DISTRICTS = {
    "1": ["12", "7", "5"],    # 台北市
    "3": ["34"]  # 新北市
}

METRO_STATIONS = {
    "100": ["4190", "4191", "4195"], # 文湖線
    "148": ["4248", "4250"] # 松山新店線
}

RENT_RANGE = (10000, 20000)     # 租金區間
MIN_PING = 10                  # 最小坪數
MAX_PING = 20                 # 最大坪數
KINDS = ["1", "2"]            # 1: 整層住家, 2: 獨立套房, 3: 分租套房
NEW_WITHIN_HOURS = 18       # 幾小時內上架的物件

SEND_LINE_MESSAGE = True
RANDOM_DELAY = True

GET_RECOMMENDS = True
GET_NORMAL = True

TEST_MODE = False  # Set to True for testing, False for production

NOT_COVER = True  # 不限屋況
ALL_SEX = True    # 不限性別
BOY_ONLY = True   # 只限男生

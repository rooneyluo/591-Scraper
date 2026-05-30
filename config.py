SEARCH_MODE = "district"  # "district" or "metro"

CITY_DISTRICTS = {
    "1": ["4", "11", "3", "7"],    # 台北市
    #"3": ["34"]
}

METRO_STATIONS = {
    "100": ["4190", "4191", "4195"], # 文湖線
    "148": ["4248", "4250"] # 松山新店線
}

RENT_RANGE = (0, 17000)     # 租金區間
MIN_PING = 0                  # 最小坪數
MAX_PING = 100                 # 最大坪數
KINDS = ["2"]            # 1: 整層住家, 2: 獨立套房, 3: 分租套房
NEW_WITHIN_HOURS = 12       # 幾小時內上架的物件

SEND_LINE_MESSAGE = True
RANDOM_DELAY = False

GET_RECOMMENDS = True
GET_NORMAL = True

TEST_MODE = False  # Set to True for testing, False for production

NOT_COVER = True  # 不限屋況
ALL_SEX = False    # 不限性別
BOY_ONLY = False   # 只限男生

OTHERS = "pet&floor=2_6,6_12,13_"
OPTIONS = "broadband"

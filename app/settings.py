import os

TELEGRAM_BOT_API_TOKEN = os.environ["TELEGRAM_BOT_API_TOKEN"]
COINGECKO_API_KEY = os.environ["COINGECKO_API_KEY"]

COIN_LIST_LINK = "https://docs.google.com/spreadsheets/d/1wTTuxXt8n9q7C4NDXqQpI3wpKu1_5bGVmP9Xz0XGSyU/edit?gid=0#gid=0"

COIN_MAP = {
    "btc": {
        "cg_id": "bitcoin",
        "symbol": "BTC",
        "name": "Bitcoin",
    },
    "eth": {
        "cg_id": "ethereum",
        "symbol": "ETH",
        "name": "Ethereum",
    },
    "other": {
        "cg_id": "bitcoin",
        "symbol": "BTC",
        "name": "Bitcoin",
    },
}
CURRENCY_MAP = {
    "usd": {
        "cg_id": "usd",
        "symbol": "USD",
        "name": "US Dollar",
        "locale": "en_US",
    },
    "sgd": {
        "cg_id": "sgd",
        "symbol": "SGD",
        "name": "Singapore Dollar",
        "locale": "en_SG",
    },
    "idr": {
        "cg_id": "idr",
        "symbol": "IDR",
        "name": "Indonesian Rupiah",
        "locale": "id_ID",
    },
    "vnd": {
        "cg_id": "vnd",
        "symbol": "VND",
        "name": "Vietnamese đồng",
        "locale": "vi_VN",
    },
}

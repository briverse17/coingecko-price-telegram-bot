"""CoinGecko module"""

import json
import logging
import os
from datetime import UTC, datetime
from typing import Dict, List

import requests
from babel.numbers import format_currency, get_currency_name
from humanize import naturaltime

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


OVERRIDES = {
    "btc": {"id": "bitcoin", "name": "Bitcoin"},
    "eth": {"id": "ethereum", "name": "Ethereum"},
}


class UnsupportedCurrency(Exception):
    """Custom Exception"""


class CoinGeckoService:
    """Work with the CoinGecko API"""

    def __init__(self, api_key: str) -> None:
        logger.info("Starting CoinGecko Service")
        self.headers = {
            "accept": "application/json",
            "x-cg-demo-api-key": api_key,
        }
        self.session = requests.Session()

        os.makedirs("cache", exist_ok=True)
        self.coins: Dict[str, List[Dict[str, str]]] = {}
        self.currencies = []
        self.get_coins_list()
        self.get_currencies_list()

    def get_coins_list(self, filepath="cache/coins_list.json"):
        """Get the list of coins available on Coin Gecko"""

        file_existed = os.path.isfile(filepath)
        data = []
        if file_existed:
            logger.info("CoinGecko Service: Loading Coins List from cache")
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            logger.info("CoinGecko Service: Requesting Coins List")
            with open(filepath, "w", encoding="utf-8") as f:
                response = self.session.get(
                    "https://api.coingecko.com/api/v3/coins/list",
                    headers=self.headers,
                    timeout=30,
                )
                data = response.json()
                json.dump(data, f, ensure_ascii=False)
        for coin in data:
            symbol, _id, name = coin["symbol"], coin["id"], coin["name"]
            entry = {"id": _id, "name": name}
            if not coin["symbol"] in self.coins:
                self.coins[symbol] = [entry]
            else:
                self.coins[symbol].append(entry)

    def get_currencies_list(self, filepath="cache/currencies_list.json"):
        """Get the list of vs_currencies available on Coin Gecko"""

        file_existed = os.path.isfile(filepath)
        data = []
        if file_existed:
            logger.info("CoinGecko Service: Loading Currencies List from cache")
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            logger.info("CoinGecko Service: Requesting Currencies List")
            with open(filepath, "w", encoding="utf-8") as f:
                response = requests.get(
                    "https://api.coingecko.com/api/v3/simple/supported_vs_currencies",
                    headers=self.headers,
                    timeout=30,
                )
                data = response.json()
                json.dump(data, f, ensure_ascii=False)
        self.currencies = data
        return self.currencies

    def check_coin(self, coin: str = "bitcoin"):
        """Check if the coin is supported by CoinGecko"""
        if coin not in self.coins:
            raise UnsupportedCurrency(f"Unsupported coin <code>{coin}</code>")
        return self.coins[coin]

    def check_currency(self, currency: str = "bitcoin"):
        """Check if the coin is supported by CoinGecko"""
        if currency not in self.currencies:
            raise UnsupportedCurrency(f"Unsupported currency <code>{currency}</code>")
        return currency

    def get_price(
        self,
        symbol: str = "btc",
        _id: str = None,
        name: str = None,
        currency: str = "usd",
        allow_override: bool = True,
        verbose: bool = False,
    ):
        """Request for the price of `coin` in `currency`"""
        coins = self.check_coin(symbol)
        _id = _id if _id else coins[0]["id"]
        name = name if name else coins[0]["name"]
        if allow_override and symbol in OVERRIDES:
            _id, name = OVERRIDES[symbol]["id"], OVERRIDES[symbol]["name"]
        currency = self.check_currency(currency)
        response = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            headers=self.headers,
            params={
                "ids": _id,
                "vs_currencies": currency,
                "include_last_updated_at": "true",
            },
            timeout=30,
        )

        result = response.json()

        if verbose:
            logger.debug(json.dumps(result))

        value = result[_id][currency]
        epoch = result[_id]["last_updated_at"]

        heading = f"<b>{name}</b>"
        result = (
            f"{heading}"
            f"\n<code>1 {symbol.upper()} = {value} {currency.upper()}</code>"
            "\n"
            f"\nLast updated: {format_time(epoch)}"
        )

        others = [c for c in coins if c["name"] != name]

        # result += f"\nOthers <code>{symbol.upper()}</code>s: \n- {others}"

        return result, others


def format_price(value: int, currency: str = "usd"):
    """Format the price in the locale of currency"""
    # _, symbol, _, locale = CURRENCY_MAP[currency].values()
    return f"<b>{format_currency(value, currency, '#,##0.00 ¤¤')}</b>"


def format_time(epoch: int):
    """Format the time of the last updated price"""
    delta = datetime.now(UTC) - datetime.fromtimestamp(epoch, tz=UTC)
    return f"<i>{naturaltime(delta)}</i>"

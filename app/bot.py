import logging

from coingecko import CoinGeckoService, UnsupportedCurrency
from settings import COIN_LIST_LINK, COINGECKO_API_KEY, TELEGRAM_BOT_API_TOKEN
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

SERVICE = CoinGeckoService(COINGECKO_API_KEY)

COIN, CURRENCY = "btc", "usd"

# Pre-assign menu text
MAIN_MENU = (
    "<b>Hi! This is the Realtime CoinGecko Price Bot.</b>"
    "\n"
    "\n<b>Usage:</b>"
    "\nCheck coin price in a currency"
    "\n/p | /price [coin] [currency]"
    "\nExample: '/p' or '<code>/price btc vnd</code>'"
    "\n"
    "\nCheck Bitcoin or Ethereum price in a currency"
    "\n/btc | /eth [currency]"
    "\nExample: '/btc' or '/eth' or '<code>/eth sgd</code>'"
    "\n"
    "\nSupported coins"
    "\n/coins"
    "\nDefault: <code>btc</code>"
    "\n"
    "\nSupported currencies"
    "\n/currencies"
    "\nDefault: <code>usd</code>"
)

# Pre-assign button text
BTC_BUTTON = f"BTC Price in {CURRENCY.upper()}"
ETH_BUTTON = f"ETH Price in {CURRENCY.upper()}"
COINS_BUTTON = "List of supported coins"
CURRENCIES_BUTTON = "List of supported currencies"

MAIN_MENU_MARKUP = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton(BTC_BUTTON, callback_data="btc")],
        [InlineKeyboardButton(ETH_BUTTON, callback_data="eth")],
        [InlineKeyboardButton(COINS_BUTTON, url=COIN_LIST_LINK)],
        [InlineKeyboardButton(CURRENCIES_BUTTON, callback_data="currencies")],
    ]
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command

    Return the usage
    """
    await update.message.reply_text(
        MAIN_MENU,
        parse_mode=ParseMode.HTML,
        reply_markup=MAIN_MENU_MARKUP,
    )
    return


async def price(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    symbol: str = None,
    _id: str = None,
    name: str = None,
    currency: str = None,
    allow_override: str = True,
) -> None:
    """Handle the /p | /price commands

    Args:
    ---
        `symbol`: str
            Symbol of the coin, e.g. btc, eth
        `_id`: str
            CoinGecko specific ID, e.g. bitcoin, ethereum
        `name`: str
            CoinGecko display name
        `currency`: str
            The currency to request for
        `allow_override`: bool
            There are coins with the same symbol.
            Here we override the two most common which is
            "btc" and "eth" to "bitcoin" and "ethereum".
            To explicitly query a coin, we feed in the `_id`
            and set this param to `False` to disable overriding.
    """

    symbol = symbol if symbol else context.args[0] if len(context.args) > 0 else COIN
    currency = (
        currency
        if currency
        else context.args[1]
        if len(context.args) == 2
        else CURRENCY
    )

    logger.info(
        "%s asked for %s price in %s",
        update.effective_user.first_name,
        name if name else symbol.upper(),
        currency.upper(),
    )
    try:
        result, others = SERVICE.get_price(symbol, _id, name, currency, allow_override)
        await context.bot.send_message(
            update.effective_chat.id, result, parse_mode=ParseMode.HTML
        )

        if others:
            msg = f"Check other coins with the same symbol <b>{symbol.upper()}</b>"
            await context.bot.send_message(
                update.effective_chat.id,
                msg,
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                c["name"],
                                callback_data="&&".join((symbol, c["id"], currency)),
                            )
                        ]
                        for c in others[:3]
                    ]
                ),
            )

    except UnsupportedCurrency as e:
        await context.bot.send_message(
            update.effective_chat.id,
            e.args[0],
            parse_mode=ParseMode.HTML,
        )


async def btc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /btc command

    Quickly get the Bitcoin price in the current currency
    """
    currency = context.args[0] if context.args and len(context.args) == 1 else CURRENCY
    await price(update, context, "btc", currency=currency)


async def eth(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /eth command

    Quickly get the Ethereum price in the current currency
    """
    currency = context.args[0] if context.args and len(context.args) == 1 else CURRENCY
    await price(update, context, "eth", currency=currency)


async def coins(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /coins command

    Return the Google Spreadsheet link to the list of coins
    """
    await context.bot.send_message(
        update.effective_chat.id,
        f"Please refer to <a href='{COIN_LIST_LINK}'>this link</a>",
        parse_mode=ParseMode.HTML,
    )


async def currencies(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /currencies command

    Return the list of `vs_currencies` from CoinGecko
    """
    await context.bot.send_message(
        update.effective_chat.id,
        (
            "Supported currencies"
            + "\n\n"
            + ", ".join([f"<code>{c}</code>" for c in SERVICE.currencies])
        ),
        parse_mode=ParseMode.HTML,
    )


async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button press"""

    await update.callback_query.answer()
    if "&&" not in update.callback_query.data:
        match update.callback_query.data:
            case "btc":
                await btc(update, context)
            case "eth":
                await eth(update, context)
            case "currencies":
                await currencies(update, context)
            case _:
                logger.debug(
                    "%s entered an unknown command '%s'",
                    update.effective_user.first_name,
                    update.callback_query.data,
                )
    else:
        # Explicit coin query
        name = None
        for row in update.callback_query.message.reply_markup.inline_keyboard:
            for button in row:
                if button.callback_data == update.callback_query.data:
                    name = button.text
                    break
            if name:
                break
        coin, _id, currency = update.callback_query.data.split("&&")
        await price(update, context, coin, _id, name, currency, False)


def main() -> None:
    """Run the bot."""

    application = Application.builder().token(TELEGRAM_BOT_API_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler(["price", "p"], price))
    application.add_handler(CommandHandler("btc", btc))
    application.add_handler(CommandHandler("eth", eth))
    application.add_handler(CommandHandler("coins", coins))
    application.add_handler(CommandHandler("currencies", currencies))
    application.add_handler(CallbackQueryHandler(handle_button))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

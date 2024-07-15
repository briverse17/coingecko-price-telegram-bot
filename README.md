# Realtime CoinGecko Price Bot

## Bot usage

Check coin price in a currency

    /p | /price [coin] [currency]

    Example: /p or /price btc vnd

Check Bitcoin or Ethereum price in a currency

    /btc | /eth [currency]
    Example: /btc or /eth or /eth sgd

Supported coins. Default: btc

    /coins

Supported currencies. Default: usd

    /currencies

## Code build

1. Get your [Telegram bot API Token](https://core.telegram.org/bots/features#botfather)
2. Get your [CoinGecko API Key](https://docs.coingecko.com/v3.0.1/reference/setting-up-your-api-key)
3. Copy `.env.example` to `.env`
4. Put the API token/key above to the corresponding variables
5. Run `docker compose up --build` (exlude the `--build` flag at your need)

#!/usr/bin/env python
from datetime import datetime, date, timedelta
from contextlib import suppress
import os
import fire

from rich import print
from rich.console import Console
from rich.columns import Columns
console = Console()

from alpaca.trading.requests import LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.client import TradingClient
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from alpaca.data.historical.option import OptionHistoricalDataClient
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest
from alpaca.data.models.snapshots import OptionsGreeks
from alpaca.data.requests import (
    OptionTradesRequest,
    OptionLatestQuoteRequest,
    OptionChainRequest,
)
from alpaca.trading.requests import (
    GetOptionContractsRequest,
    GetAssetsRequest,
    MarketOrderRequest,
    GetOrdersRequest,
)
from alpaca.trading.enums import (
    AssetStatus,
    AssetClass,
    OrderSide,
    OrderType,
    TimeInForce,
    ContractType,
    PositionSide,
    PositionIntent,
)
from alpaca.common.exceptions import APIError

from utils import *
from tables import *
from optionchain import *


def print_banner():
    print("Welcome to Alpaca-Wheel!")
    print("========================")
    print()

def setup_clients(paper: bool | None = None):
    from dotenv import load_dotenv
    load_dotenv()  # take environment variables from .env.

    if paper is None:
        paper = bool(os.environ.get("ALPACA-PAPER", True))

    if paper:
        api_key = os.environ.get("PAPER-ALPACA-API-KEY")
        secret_key = os.environ.get("PAPER-ALPACA-SECRET-KEY")
    else:
        api_key = os.environ.get("ALPACA-API-KEY")
        secret_key = os.environ.get("ALPACA-SECRET-KEY")

    # keys required for stock historical data client
    stock_client = StockHistoricalDataClient(api_key, secret_key)
    option_client = OptionHistoricalDataClient(api_key, secret_key)
    trade_client = TradingClient(
                        api_key=api_key,
                        secret_key=secret_key,
                        paper=paper,
                    )

    return (stock_client, option_client, trade_client)

# TODO: argparse/click/fire@click.command()
def main(
        symbol: str,
        *,
        delta_lte: float | str = 0.31,
        must_earn: int | float = 100,
        leap: bool  = False,
        paper: bool | None =None,
        dryrun: bool = False,
        danger: bool = False,
    ):
    """ Run the Wheel Strategy

    :param symbol: the stock you want to own
    :param delta_lte: sell options <= delta
    :param must_earn: FAIL if premium is not enough (try again later (NO REALLY! WAIT!))
    :param leap: Collaterize with a Long call LEAP (Poor Mans Covered Call) Instead of CSP
    :param paper: Are you using a paper account?
    :param dryrun: Dont actually execute trades
    :param danger: Sell even if you already have a short position (USES MARGIN! testing only)

    :returns str: UUID of trade for later lookup 

    """
    print_banner() # TODO: dont show this every time

    if paper is None:
        paper = bool(os.environ.get("ALPACA-PAPER", True))

    (stock_client, option_client, trade_client) = setup_clients(paper=paper)


    # Get our account information.
    account = trade_client.get_account()
    console.print(get_account_overview_table(account, paper=paper))

    # Get a list of all of our positions.
    portfolio = trade_client.get_all_positions()
    console.print(get_positions_table(portfolio))

    selected_asset = symbol.upper()
    print(f"SELECTED ASSET: {selected_asset}")
# search for SMCI
    asset = trade_client.get_asset(selected_asset)

    # Do we have short options?
    # if so, bail now!
    for position in portfolio:
        if position.asset_class == AssetClass.US_OPTION \
        and position.side == PositionSide.SHORT \
        and position.symbol.startswith(asset.symbol):
            print(f"[FAIL] you have an open short position! [{option_name_coloring(position.symbol)}]")
            if not danger:
                print("[FAIL] Exiting!!!!")
                exit(4);

    if not asset.tradable:
        print(f'[{selected_asset}] NOT TRADEABLE! [[ERROR]]')
        exit(1);
    else:
        asset_params = StockLatestQuoteRequest(symbol_or_symbols=[selected_asset])
        latest_quote = stock_client.get_stock_latest_quote(asset_params)[selected_asset]
        bid, ask = (latest_quote.bid_price, latest_quote.ask_price)
        #print(f"bid/ask @[{latest_quote.bid_price}/{latest_quote.ask_price}]")
        #print(f"PREFERRED STRIKE: {preferred_strike_put}")
        console.print(get_bid_ask_table(selected_asset, bid, ask))

    # DEFAULT: assume we have never run before (until proven otherwise),
    # so we must first sell a PUT!
    mode = ContractType.PUT

    # Get our position in SMCI.
    with suppress(APIError):
        # stock position
        sp = trade_client.get_open_position(selected_asset)
        print(f"\n{selected_asset} Position (detailed)\n======================")
        print(f"{sp.qty_available} {sp.symbol} @ {sp.avg_entry_price} [{sp.unrealized_pl}]")

        if int(sp.qty_available) >= 100:
            # we need not acquire 100 shares, we already have them!
            mode = ContractType.CALL

    # AT THIS POINT:
    #   - we have a good understanding of our account status
    #   - we have decided whether to sell a PUT or CALL

    print(f"current Mode: {mode.value}")
    chain_request = get_option_chain_request(
                asset.symbol,
                mode,
                bid,
                ask,
                account
    )

    #res = trade_client.get_option_contracts(chain_request)
    #print_option_chain_simple_openinterest(res)

    chain_response = option_client.get_option_chain(chain_request)
    print("option chain retrieved!")
    print("Filtering acceptable contracts...\n")

    x = [contract for _, contract in chain_response.items()]
    x.sort(key = lambda item: item.latest_quote.bid_price)
    x_filtered = filter(lambda c: c.greeks is not None and abs(c.greeks.delta) < abs(delta_lte), x)
    x_list = list(x_filtered)

    console.print(get_option_chain_with_greeks(x_list))

    if not x_list:
        print("No acceptable contracts found!")
        print("this can be for any number of reasons including:")
        print("  - bad expiration date")
        print("  - unable to fetch greeks")
        print("  - (etc)")
        exit(2)

    highest_bid = x_list[-1] # the assumption is x_list is sorted by bid, so this is the highest bid

    new_limit_price = round(highest_bid.latest_quote.bid_price - 0.02, 2)
    if new_limit_price*100 < must_earn: # $100 at least
        # TODO: Don't hardcode this, make it adjustable!
        print(f"not enough premium! {new_limit_price*100} < {must_earn}")
        exit(3);

    limit_order_data = LimitOrderRequest(
                        symbol=highest_bid.symbol,
                        limit_price= new_limit_price,
                        qty=1,
                        side=OrderSide.SELL,
                        time_in_force=TimeInForce.DAY,
                        position_intent=PositionIntent.SELL_TO_OPEN,
                       )

    # Limit order
    print(f"executing [SELL {option_name_coloring(highest_bid.symbol)}] for >${new_limit_price*100:.2f}")
    print(limit_order_data)

    if not dryrun:
        limit_order = trade_client.submit_order( order_data=limit_order_data)
        print(f"Order Submitted! id: {limit_order.id}")
    else:
        print("DRY RUN! No orders submitted")


    # TODO: queue a buyback at 10% the premium recieved
    # TODO: Notify discord/slack/something else

if __name__ == "__main__":
    fire.Fire(main)

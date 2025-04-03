from rich.table import Table
from rich import print
from utils import *

from alpaca.data.models.snapshots import OptionsGreeks

def print_option_chain_simple_openinterest(res):
    def option_list_item(i):
        return f"{option_name_coloring(i.symbol)} {i.underlying_symbol} {i.type.upper()} {i.strike_price} [{i.open_interest}]"

    print("==== Options Contracts [Open Interest] ========")
    for i in res.option_contracts:
        print(option_list_item(i))
    print()

def get_account_overview_table(account, paper=False):
    balance_change = float(account.equity) - float(account.last_equity)

    # Display Account
    table = Table(title="Account Overview")
    table.add_column("Cash", justify="right", style="green", no_wrap=True)
    table.add_column("Todays P/L", style="magenta")
    table.add_column("Paper")
    table.add_row(
            green_or_red(account.cash),
            green_or_red(round(float(balance_change), 2)),
            str(paper)
    )
    return table

def get_positions_table(portfolio):
    portfolio_table = Table(title="Portfolio")
    portfolio_table.add_column("Quantity")
    portfolio_table.add_column("Available")
    portfolio_table.add_column("Symbol")
    portfolio_table.add_column("Type")
    portfolio_table.add_column("Long/Short")
    portfolio_table.add_column("P/L")

    for position in portfolio:
        portfolio_table.add_row(
                green_or_red(position.qty),
                green_or_red(position.qty_available),
                option_name_coloring(position.symbol),
                str(position.asset_class.value),
                long_or_short_color(position.side.value),
                green_or_red(position.unrealized_pl),
        )
    return portfolio_table

def get_bid_ask_table(stock, bid, ask, preferred_strike=""):
        table = Table()
        table.add_column("symbol")
        table.add_column("bid")
        table.add_column("ask")
        table.add_column("Desired Strike")
        table.add_row(
                str(stock),
                str(bid),
                str(ask),
                str(preferred_strike),
        )
        return table

def get_option_chain_with_greeks(chain_list):
    chain = Table("bid", "symbol", *OptionsGreeks.model_fields.keys(), title="Option Chain")
    for contract in chain_list:
        if contract.greeks:
            greeks = *[str(v) for k,v in dict(contract.greeks).items()],
        else:
            greeks = [" "," "," "," "," "]
        try:
            chain.add_row(
                f"{contract.latest_quote.bid_price:.2f}",
                option_name_coloring(contract.symbol),
                *greeks
            )
        except Exception as e:
            breakpoint()
    return chain

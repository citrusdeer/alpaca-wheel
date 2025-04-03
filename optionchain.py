from alpaca.data.requests import OptionChainRequest
from alpaca.trading.enums import (
    AssetStatus,
    ContractType,
)
from datetime import date, timedelta

def get_option_chain_request(stock, mode, bid, ask, account=None, sp=None, profit=1.00):
    consider = []
    if account:
        consider = [ float(account.cash)/100, float(account.buying_power)/100 ]

    if mode == ContractType.PUT:
        options = {"strike_price_lte": str(round(min(float(bid*0.95), *consider), 2))}
    else:
        if getattr(sp, "cost_basis", None):
            options = {"strike_price_gte": str((float(sp.cost_basis)/100)*profit)}
            print(f"cost basis: {sp.cost_basis}")
        else:
            options = {"strike_price_gte": str(round(float(ask*1.05), 2))}

    chain_request = OptionChainRequest(
                        underlying_symbol=stock,
                        status = AssetStatus.ACTIVE,
                        expiration_date_lte = date.today() + timedelta(days=7), # 9 days from toda
                        **options,
                        type = mode,
                        limit=100,
                    )

    return chain_request

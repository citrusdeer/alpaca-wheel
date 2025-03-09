# Alpaca Wheel


> [!WARNING]
> THIS IS THEORETICAL!
> I HAVE NOT BACKTESTED THIS,
> AND THERE ARE TOO MANY POSSIBLE VARIABLES!
> YOU WILL PROBABLY LOSE MONEY!
>
> and I take absoutely zero responsibility for that.
> This code can trade real money!
> Do not run code you do not understand!
> It's your fault if you do!
> You have been warned!

How the Wheel Strategy works!
---
> [!NOTE]
> MAKE SURE YOU PICK A STOCK YOU LIKE AND ARE COMFORTABLE HOLDING THROUGH BEAR MARKETS!

1. Start with cash
   -  sell a short dated, slightly OTM PUT, collect premium.
   -  If unassigned, repeat step 1 until assigned! Free Premium!

2. Youve Been assigned and are holding shares.
      - sell a short dated CALL (Strike MUST be no less than cost basis from PUT)
        - Yes, Sometimes this means holding shares that continue to decline, selling low delta options for little premium. Dont take risks and sell CALLS below cost basis!
      - Repeat until assigned, return to PUTS



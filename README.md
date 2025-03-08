# Alpaca Wheel

======= WARNING! ==========
THIS IS THEORETICAL!
I HAVE NOT BACKTESTED THIS,
AND THERE ARE TOO MANY POSSIBLE VARIABLES!
YOU WILL PROBABLY LOSE MONEY!

and I take absoutely zero responsibility for that.
This code can trade real money!
Do not run code you do not understand!
It's your fault if you do!
You have been warned!
===============================

How the Wheel Strategy works!
(MAKE SURE YOU PICK A STOCK YOU LIKE AND ARE COMFORTABLE HOLDING THROUGH BEAR MARKETS!)

Start with cash
      1. sell a short dated, slightly OTM PUT, collect premium.
      2. If unassigned, repeat step 1 until assigned! Free Premium!

Youve Been assigned and are holding shares.
      1. sell a short dated CALL (Strike MUST be no less than cost basis from PUT)
        - Yes, Sometimes this means holding shares that continue to decline, selling low delta options for little premium. Dont take risks and sell CALLS below cost basis!
      2. Repeat until assigned, return to PUTS



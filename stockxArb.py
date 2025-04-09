"""
Stock X has a bid feature where you can see what buyers are instantly willing to pay. Meaning if the bid is there and you can ship the item within two days, the money is there. 
Problem
- Most bids are severely below the asking price. 
- Takes a lot of time to look through the bids of every item
- Check P&L with your cost and final payout price, 
- Checking how close bids are to worth / asking price
Solution
- Scrape active bids and find bids that are as close to the average asking price
- find bids that are above previous or have seen increase, be carful because can increase, then decrease then go higher. 

-Is it how close to asking price?, What is the optimal distance and what drives 
-Or how close to (last price, average price), can use seaborn to decide which is more indicitive of value 
- Do we make sure there is a price premium from retail 

Basically finding stockX arbitrage opportunities. 

How to sell:
- use for myself to figure out what products to sell
- Sell this service as a discord or private twitter, where i reveal arbatrage opportunities, monthly payment for acess on alpha

Ex
what was made the CH LS tee L a good model
- retail for 375 - 425
- Bid for 800
- Usually sells for 1000
- Rare to find an instantanius buyer

Data we need
- highest bid / bids
- average price, last price
- average asks / last ask 

"""
import pandas as pd 
import math
import requests

#https://api.stockx.com/v2/catalog/products/{productId}/market-data?currencyCode=USD

url = "#https://api.stockx.com/v2/catalog/products/air-jordan-1-retro-low-og-sp-travis-scott-medium-olive/market-data?currencyCode=USD"
url_text = requests.get(url).text    
url_text

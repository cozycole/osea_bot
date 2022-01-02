/* 
Before sending offers, a profitable margin must be found.

https://support.opensea.io/hc/en-us/articles/360061699514-Who-pays-the-gas-fees-
    Buyers pay the gas fees when purchasing fixed-price items. <-- Sell fees unless I create a fixed price buy item.
    Sellers pay the gas when accepting offers. <-- So no gas fees on buy? 

Assuming: 2.5% OpenSea + 5% Royalties + 10% Taxes (less than 10,000 in income) + Sell Gas Fees

If we wanted to get a closer estimate, we would determine the variation in price over the last X time 
(X = offer time).

1) Get current price of ETH (maybe see if there's an option for past x variation)
2) Get floor price of desired collection
3) 1 - 0.175 - (gas price * sale gas units) / floor price => Offer Margin
*/

var DESIRED_PROFIT = 0.05;

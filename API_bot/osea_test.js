import * as Web3 from "web3";
import { OpenSeaPort, Network } from "opensea-js";

process.env.NODE_TLS_REJECT_UNAUTHORIZED = "0";

const provider = new Web3.providers.HttpProvider(
  "https://rinkeby.infura.io/v3/66c9d16b8c31444c80c4bd38380b9e90"
);
const contract_address = "0x0a62cfdd44235042e78e63e0e4f51a187787af4e";
var curr_tokenId = 58;
const seaport = new OpenSeaPort(provider, {
  networkName: Network.Rinkeby,
});
console.log("Seaport Instantiated");

const accountAdd = "0x64d3c5eb0310c147f3ec7429e2c3fecebda6add2";
const call = async () => {
  const bid_asset = {
    tokenAddress: contract_address,
    tokenId: curr_tokenId,
  };
  const offer = await seaport.createBuyOrder({
    asset: bid_asset,
    accountAddress: accountAdd,
    // Value of the offer, in units of the payment token (or wrapped ETH if none is specified):
    startAmount: 0.3,
  });
  console.log(offer.expirationTime);
};

call()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });

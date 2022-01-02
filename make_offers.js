const HDWalletProvider = require("@truffle/hdwallet-provider");
const Web3 = require("web3");
const opensea = require("opensea-js");
const https = require("https");

process.env.NODE_TLS_REJECT_UNAUTHORIZED = "0";

// RUNTIME VARIABLES
var EXPIRATIONTIME = process.argv[2]; // amount in hours
var CURRENT_INDEX = process.argv[3];
var COLLECTION_COUNT = 500; // number of nfts in a collection
var MY_ADDRESS = "0x1fFB6F65c0045052adf612b51f40D9b900C15AA0";
var TOKEN_ADDRESS = "0xcC14dd8E6673fEE203366115D3f9240b079a4930";
var COLLECTION_URL =
  "https://testnets-api.opensea.io/collection/crypto-dino-v3"; //https://api.opensea.io/collection/
var FLOOR_PRICE = 0;

let HDprovider = new HDWalletProvider({
  privateKeys: [process.env.PRIV_KEY],
  providerOrUrl:
    "https://rinkeby.infura.io/v3/66c9d16b8c31444c80c4bd38380b9e90",
});

async function getName() {
  return new Promise(function (resolve, rejct) {
    https
      .get(COLLECTION_URL, (res) => {
        var rawData = "";
        res.on("data", (d) => {
          rawData += d;
        });

        res.on("end", () => {
          try {
            const parsedData = JSON.parse(rawData);
            FLOOR_PRICE = parsedData["collection"]["stats"]["floor_price"];
            console.log("FLOOR PRICE TYPE ", typeof FLOOR_PRICE);
            console.log("NAME: ", parsedData["collection"]["name"]);
            console.log(
              "FLOOR PRICE: ",
              parsedData["collection"]["stats"]["floor_price"]
            );
            resolve();
          } catch (e) {
            console.log("ERROR:", e);
          }
        });
      })
      .on("error", (e) => {
        console.error(e);
      });
  });
}
const seaport = new opensea.OpenSeaPort(HDprovider, {
  networkName: opensea.Network.Rinkeby,
});

const make_offers = async () => {
  //Get Collection Floor Price and Name of Collection
  var x = await getName();
  bid_price = 0.8 * FLOOR_PRICE;
  console.log("BID PRICE TYPE", typeof bid_price);
  console.log("BID OFFER AT ", bid_price);
  // NEED TO FIND HOW MANY TOKENS ARE IN A COLLECTION DYNAMICALLY
  for (var i = CURRENT_INDEX; i < COLLECTION_COUNT; i++) {
    const offer = await seaport
      .createBuyOrder({
        asset: {
          tokenAddress: TOKEN_ADDRESS,
          tokenId: i,
        },
        accountAddress: MY_ADDRESS,
        startAmount: bid_price,
        expirationTime: Math.round(
          Date.now() / 1000 + 60 * 60 * EXPIRATIONTIME // should just be an hour
        ),
      })
      .then(() => {
        console.log("OFFER MADE ON NFT");
      })
      .catch((err) => {
        console.log("FAILED ORDER! ", err);
        return;
      });
    //console.log(offer);
  }
};

make_offers()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });

const HDWalletProvider = require("@truffle/hdwallet-provider");
const Web3 = require("web3");
const opensea = require("opensea-js");
const https = require("https");
const { rejects } = require("assert");

process.env.NODE_TLS_REJECT_UNAUTHORIZED = "0";

const TEST_INFURA =
  "https://rinkeby.infura.io/v3/66c9d16b8c31444c80c4bd38380b9e90";
const MAIN_INFURA =
  "https://mainnet.infura.io/v3/66c9d16b8c31444c80c4bd38380b9e90";

// RUNTIME VARIABLES
const EXPIRATIONTIME = process.argv[2]; // amount in hours
var COLLECTION_COUNT = 7777; // number of nfts in a collection
var TEST_ADDRESS = "0x1fFB6F65c0045052adf612b51f40D9b900C15AA0";
var MAIN_ADDRESS = "0xB91D96cA297E06f0Db299Eb067B236BCf37Feb29";
var MY_ADDRESS = MAIN_ADDRESS;
var DINO_ADDRESS = "0xcC14dd8E6673fEE203366115D3f9240b079a4930";
var APES_ADDRESS = "0x90cA8a3eb2574F937F514749ce619fDCCa187d45";
var TOKEN_ADDRESS = APES_ADDRESS;
var TEST_COLLECTION_URL =
  "https://testnets-api.opensea.io/collection/crypto-dino-v3"; //https://api.opensea.io/collection/
var MAIN_COLLECTION_URL = "https://api.opensea.io/collection/gamblingapes";
var COLLECTION_URL = MAIN_COLLECTION_URL;
var FLOOR_PRICE = 0;

let HDprovider = new HDWalletProvider({
  privateKeys: [process.env.PRIV_KEY],
  providerOrUrl: MAIN_INFURA,
});

async function getName() {
  return new Promise(function (resolve, reject) {
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
            reject();
          }
        });
      })
      .on("error", (e) => {
        console.error(e);
      });
  });
}
const seaport = new opensea.OpenSeaPort(HDprovider, {
  networkName: opensea.Network.Main,
});

const make_offers = async () => {
  //Get Collection Floor Price and Name of Collection
  var x = await getName();
  bid_price = 0.8 * FLOOR_PRICE;
  console.log("BID PRICE TYPE", typeof bid_price);
  console.log("BID OFFER AT ", bid_price);
  const time = Math.round(Date.now() / 1000 + 60 * 60 * EXPIRATIONTIME);
  // NEED TO FIND HOW MANY TOKENS ARE IN A COLLECTION DYNAMICALLY
  var endLoop = false;
  while (true) {
    if (endLoop) {
      return;
    }
    var randToken = Math.floor(Math.random() * COLLECTION_COUNT) + 1;
    const offer = await seaport
      .createBuyOrder({
        asset: {
          tokenAddress: TOKEN_ADDRESS,
          tokenId: randToken,
        },
        accountAddress: MY_ADDRESS,
        startAmount: bid_price,
        expirationTime: time, // should just be an hour if EXPIRATION == 1
      })
      .then(() => {
        console.log("OFFER MADE ON NFT");
      })
      .catch((err) => {
        console.log("FAILED ORDER! ", err);
        /*if (
          err.includes(
            "Outstanding order to wallet balance ratio exceeds allowed limit."
          )
        ) {
          console.log(
            "INCLUDE BOOL:",
            err.includes(
              "Outstanding order to wallet balance ratio exceeds allowed limit."
            )
          );
          endLoop = true;
        }*/
      });
  }
};

make_offers()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });

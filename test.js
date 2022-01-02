const HDWalletProvider = require("@truffle/hdwallet-provider");
const Web3 = require("web3");
const opensea = require("opensea-js");

process.env.NODE_TLS_REJECT_UNAUTHORIZED = "0";

let MY_ADDRESS = "0x1fFB6F65c0045052adf612b51f40D9b900C15AA0";

/*const provider = new Web3.providers.HttpProvider(
  "https://rinkeby.infura.io/v3/66c9d16b8c31444c80c4bd38380b9e90"
);*/

let HDprovider = new HDWalletProvider({
  privateKeys: [process.env.PRIV_KEY],
  providerOrUrl:
    "https://rinkeby.infura.io/v3/66c9d16b8c31444c80c4bd38380b9e90",
});

const seaport = new opensea.OpenSeaPort(HDprovider, {
  networkName: opensea.Network.Rinkeby,
});

const call = async () => {
  let tokenAddress = "0xcC14dd8E6673fEE203366115D3f9240b079a4930";
  for (let i = 1; i < 2; i++) {
    const offer = await seaport
      .createBuyOrder({
        asset: {
          tokenAddress: tokenAddress,
          tokenId: i,
        },
        accountAddress: MY_ADDRESS,
        startAmount: 0.3,
        expirationTime: Math.round(Date.now() / 1000 + 60 * 60), // should just be an hour
      })
      .then((i) => {
        console.log(`OFFER MADE ON TOK_ID ${i} `);
      })
      .catch(() => {
        console.log("FAILED ORDER!");
      });
    console.log(offer);
  }
};

call()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });

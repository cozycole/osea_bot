const ethers = require("ethers");

const itx = new ethers.providers.InfuraProvider(
  "rinkeby",
  "66c9d16b8c31444c80c4bd38380b9e90"
);

const signer = new ethers.Wallet(process.env.PRIV_KEY, itx);
console.log(`Signer public address: ${signer.address}`);

async function getBalance() {
  response = await itx.send("relay_getBalance", [signer.address]);
  console.log(`Your current ITX balance is ${response.balance}`);
}

async function deposit(signer) {
  const tx = await signer.sendTransaction({
    // ITX deposit contract (same address for all public Ethereum networks)
    to: "0x015C7C7A7D65bbdb117C573007219107BD7486f9",
    // Choose how much ether you want to deposit to your ITX gas tank
    value: ethers.utils.parseUnits("1", "ether"),
  });
  // Waiting for the transaction to be mined
  await tx.wait();
}

//deposit(signer);
getBalance();

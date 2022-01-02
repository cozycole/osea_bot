const https = require("https");

process.env.NODE_TLS_REJECT_UNAUTHORIZED = "0";

https
  .get("https://testnets-api.opensea.io/collection/crypto-dino-v3", (res) => {
    /*console.log("statusCode:", res.statusCode);
    console.log("headers:", res.headers);*/
    console.log(res);
    var rawData = "";
    res.on("data", (d) => {
      rawData += d;
    });

    res.on("end", () => {
      try {
        const parsedData = JSON.parse(rawData);
        console.log(parsedData);
        console.log("NAME: ", parsedData["collection"]["name"]);
        console.log(
          "FLOOR PRICE: ",
          parsedData["collection"]["stats"]["floor_price"]
        );
      } catch (e) {
        console.log("ERROR");
      }
    });
  })
  .on("error", (e) => {
    console.error(e);
  });

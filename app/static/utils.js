$(document).ready(() => {

  var qrcode = new QRCode(document.getElementById("qrcode"), {
	width        : 128,
	height       : 128,
    useSVG       : true,
	correctLevel : QRCode.CorrectLevel.H
  });

  qrcode.makeCode(short_url);


});

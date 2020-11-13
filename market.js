//__________________Handles buy/sell buttons on click ______________
//___opens POPUP window, shows quote data and toggles b/s button____
$(document).click(function(e) {
  event.preventDefault()
  parentElem = e.target.parentNode;

  btnID = parentElem.className;
  // Handle only if BUY or SELL buttons are pressed
  if (btnID === "btnBuy" || btnID === "btnSell") {
    ticker = parentElem.parentNode.parentNode.id;

    // Shows the pop up window
    modal.style.visibility = "visible";

    var nopad = parentElem.parentNode.className;
    getQuoteData(nopad, ticker)

    // Activates SELL or BUY button in POPUP window
    document.getElementById(btnID).className += " active";
    document.getElementById("tickerInput").value = ticker;    
  }
})
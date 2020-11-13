//_________Submit button events after preventDefault__________
$("a[name='goBtn']").click(function() {
  var text = $(this).text();

  if (text === "Market (current)") {
    $("#goWallet").attr("action", "/market");
  }
  else if (text == "Wallet") {
    $("#goWallet").attr("action", "/wallet");
  }
  else if (text == "Account Activity") {
    $("#goWallet").attr("action", "/wallet");
  }
  else if (text == "Logout") {
    $("#goWallet").attr("action", "/logout");
  }

  $("#goWallet").submit()
})

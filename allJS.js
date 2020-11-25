
  function doEver(id) {
    let yAxis = {};
    let xAxis = {};

    getData(id);
  }
       
  function getData(entry) {
      fetch("http://127.0.0.1:5000/getHistoricalData", {
      method: "POST",
      credentials: "include",
      body: JSON.stringify(entry),
      cache:"no-cache",
      headers: new Headers({
      "content-type": "application/json"
      })
    })
    .then(response => response.json())
    .then(data => {   
      xAxis = data["xAxis"]
      yAxis = data["yAxis"]
      
      resetGraph();
      doGraph(xAxis, yAxis, entry)      
    })
  }    

  function doGraph(xData, yData, ticker) {
    var config = {
			type: 'line',
			data: {
				labels: xData,
				datasets: [{
					label: 'Dataset: ' + ticker,
					backgroundColor: "lightgray",
					borderColor: "black",
					data: yData,
					fill: false,
				}]
			},
			options: {
				responsive: true,
				title: {
					display: true,
					text: '5 year period historic performance'
				},
				tooltips: {
					mode: 'index',
					intersect: false,
				},
				hover: {
					mode: 'nearest',
					intersect: true
				},
				scales: {
					xAxes: [{
						display: true,
						scaleLabel: {
							display: true,
							labelString: 'Month'
						}
					}],
					yAxes: [{
						display: true,
						scaleLabel: {
							display: true,
							labelString: 'Value'
						}
					}]
				}
			}
		};
  var ctx = document.getElementById('canvas').getContext('2d');
  window.myLine = new Chart(ctx, config);
  }

  function resetGraph() {
  document.getElementById("canvas").remove();

  var divG = document.getElementById("GRAPH");
  var canvas = document.createElement("canvas");

  divG.appendChild(canvas);

  canvas.setAttribute("id", "canvas");
  canvas.setAttribute("width", "500px");
  canvas.setAttribute("height", "500px");
  }

  

//____________Submits form that handles buy operation_____________
function buyOrder() {
  const buyForm = document.getElementById("buyForm");  
  buyForm.submit()
}

//_________Makes pop up windows appear. Windows to process orders.
function toggleModal(id) {
  const qModal = document.getElementById("qModal");
  const mModal = document.getElementById("mModal");
  const mLabel = document.getElementById("mLabel");

  document.getElementById("tickerInput").value = mModal.value;

  if (mModal.value === "") {
    mLabel.innerHTML = "You need to insert a ticket symbol to continue!"
  }
  else {
    event.preventDefault()
    if (modal.style.visibility === "hidden") {
      modal.style.visibility = "visible";
      qModal.value = mModal.value;
    }
    else {
      modal.style.visibility = "hidden";
    }
  }
  
  if (id === "orderBtn") {
    getQuoteData();
  }
}

//__________Gets price and company name from the server
function getQuoteData(id, ticknoPad) {
  event.preventDefault()

  if (id !== "noPad") {     
    if (mModal.value === "") {
      mLabel.innerHTML = "You need to insert a ticket symbol to continue!"
      mLabel.style.visibility = "visible";
      return;
    }
  }

  if (id === "noPad") {
    ticker = ticknoPad;
  }
  else {
    ticker = document.getElementById("mModal").value;
  }  

  fetch("http://127.0.0.1:5000/getPrice", {
    method: "POST",
    credentials: "include",
    body: JSON.stringify(ticker),
    cache:"no-cache",
    headers: new Headers({
      "content-type": "application/json"
    })
  })
  .then(response => response.json())
  .then(data => {

    price = data["price"];
    companyName = data["companyName"];

    both = price + "/" + companyName;

    if (id === "checkPriceBtn") {
      document.getElementById("mLabel").innerText = companyName + " current share price is $" + price + ".";
      mLabel.style.visibility = "visible";
    }
    else {
      ytdChange = data["ytdChange"];

      document.getElementById("superLabel").innerText = "The current price of " + companyName + " is: " + price + "."; 
      document.getElementById("labelYTD").innerText = "52 Week Change: " + ytdChange + "%.";
      document.getElementById("nameInput").value = both;
      alert(document.getElementById("nameInput").value);
    }   

  })
}


//_________________Hides pop up windows from load__________________
let modal = document.getElementById("bgmodal");
modal.style.visibility = "hidden";

$("#closeModal").click(function() {
  miniToggleModal()
})

//_____Closes the POPUP window and resets buy/sell btn toggle_____
function miniToggleModal() {
  modal.style.visibility = "hidden";
  document.getElementById("btnSell").className = "mktBtn";
  document.getElementById("btnBuy").className = "mktBtn";
}

//_________Activates BUY and SELL button in modal window________
function btnActivated(id) {
  var other = "";

  if (id === "btnBuy") {
    other = "btnSell";
  }
  else {
    other = "btnBuy";
  }

  var toActive = document.getElementById(id);
  var toDesactive = document.getElementById(other);

  var classNameActive = toActive.className;
  var classNameDesactive = toDesactive.className;

  if (classNameActive.match(/active/) === null) {
    toActive.className += " active";
  }

  if (classNameDesactive.match(/active/) !== null) {
    toDesactive.className = "mktBtn";
  }
}



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

const logged = document.getElementById("loggedIn");

if (logged !== null) {

const logBtn = document.getElementById("logBtn");
const regBtn = document.getElementById("regBtn");
const logOBtn = document.getElementById("logOBtn");

logBtn.style.visibility = "hidden";
regBtn.style.visibility = "hidden";
regBtn.style.display = "none";

logOBtn.style.visibility = "visible";
logOBtn.style.display = "inline";
}

/* _____ SETS DISPLAY FLEX IN EXPENSE TAB ____*/
  function displayFlex(element) {
  
    const expenseTab = document.getElementById("expenses");

    if (element.id == "expensesButton") {
      expenseTab.style.display = "flex";
    }
    else {
      expenseTab.style.display = "none";
    }    
  }
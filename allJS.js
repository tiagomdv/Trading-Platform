 /*___________________ ACCOUNT _________________________*/

  window.onload = function() {
    buildPieChart()
  }


  /* _____ CREATES ROWS, GRAPH AND UPDATES DATABASE ____*/
  function createRow() {
    event.preventDefault()

    data = updateDB()
    buildPieChart()

    const tablebody = document.querySelector(".table-body");
    const newTr = document.createElement("tr");
    const labelAddExp = document.querySelector(".labelAddExp");

    if (data[0] === "ERROR") {
      labelAddExp.innerHTML = "You can´t leave any blank fields!";
      labelAddExp.style.visibility = "visible";
    }
    else {
      for (i = 0; i < 4; i++) {
        const newTd = document.createElement("td");
        newTd.innerHTML = data[i];
        newTr.appendChild(newTd);
        newTr.className = "td-market";
      }
      tablebody.appendChild(newTr);
      labelAddExp.innerHTML = "You must reload page to update summary table!";
      labelAddExp.style.visibility = "visible";
      document.querySelector(".button-changes-expenses-1").style.visibility = "visible";
    }
  }


  /* _____ GETS DB DATA AND BUILDS PIE CHART ____*/
  function buildPieChart() {
    /*_ACCESSES SERVER AND UPDATE EXPENSES TABLE DB_*/
    fetch("http://127.0.0.1:5000/getDataDB", {
      method: "GET"
    })
      .then(response => response.json())
      .then(data => {
        let label = []
        let dataset = []

        const colors = ["#81b29a", "#2a9d8f", "#457b9d", "#1d3557", "#14213d", "#dee2ff", "#cbc0d3", "#64653", "#6b705c", "#d4a373"];

        data.forEach(x => {
          label.push(x[0]);
          dataset.push(x[1]);
        })

        var ctx = document.getElementById('canvas').getContext('2d');
        var myPieChart = new Chart(ctx, {
          type: 'pie',
          data: {
            labels: label,
            datasets: [{
              data: dataset,
              backgroundColor: colors,
              borderColor: "lightgray"
            }]
          },
          options: {
            title: {
              text: "Expenses Summary",
              fontSize: 18,
              fontColor: "#00b4d8",
              display: true
            },
            responsive: true,
            legend: {
              labels: {
                fontColor: "#17c3b2"
              }
            }
          }
        })
      })
  }


  /* _____ACESS SERVER TO UPDATE DATABASE____*/
  function updateDB() {

    let today = new Date().toISOString().slice(0, 10);
    let data = [today, 0, 0, 0];
    let i = 0;
    const buildData = document.querySelectorAll(".buildData");

    buildData.forEach(x => {
      if (x.value === "") {
        data[0] = "ERROR";
      }
      data[i + 1] = x.value;
      i += 1;
    })

    resetGraph()

    if (data[0] !== "ERROR") {
      /*_ACCESSES SERVER AND UPDATE EXPENSES TABLE DB_*/
      fetch("http://127.0.0.1:5000/updateDB", {
        method: "POST",
        body: JSON.stringify(data),
        headers: new Headers({
          "content-type": "application/json"
        })
      })
    }

    return data;
  }

  /* _________________ RESETS PIE CHART ________________*/
  function resetGraph() {
    document.getElementById("canvas").remove();

    var divG = document.getElementById("pie-chart");
    var canvas = document.createElement("canvas");

    divG.appendChild(canvas);

    canvas.setAttribute("id", "canvas");
    canvas.setAttribute("width", "500px");
    canvas.setAttribute("height", "500px");
  }


  /* _____ ENABLES AND DISABLES PASSWORD FIELDS ____*/
  function toggleInputPass() {
    event.preventDefault()
    const inputPass = document.querySelectorAll(".inputPass")
    const label = document.getElementById("labelTC");

    inputPass.forEach(x => {
      if (x.disabled == true) {
        x.disabled = false;
        x.classList.add("input-enabled");
        label.innerHTML = "Press Save Changes to save password!";
        label.style.display = "block";
      }
      else {
        x.disabled = true;
        x.classList.remove("input-enabled");
        label.style.display = "none";
      }
    })
  }


  /* _____ SUBMITS FORM IF INPUTS ARE CORRECTLY FILLED ____*/
  function submitIF() {
    event.preventDefault()

    const initCash = document.getElementById("initCash")
    const saveChanges = document.getElementById("saveChanges")
    const invalidcheck = document.getElementById("invalidCheck")
    const labelTC = document.getElementById("labelTC")
    let isfalse = 0

    if (invalidcheck.checkValidity() === false) {
      labelTC.innerHTML = "You need to agree with the terms and conditions to continue!"
      isfalse = 1;
    }

    if (initCash !== null) {
      if (initCash.checkValidity() === false) {
        labelTC.innerHTML = "In your first login you must set an initial cash ammount!"
        isfalse = 1;
      }
    }

    const inputPass = document.querySelectorAll(".inputPass")
    let checkPass = 0
    let counter = 0
    inputPass.forEach(x => {
      if (counter == 0) {
        checkPass = x.value
        counter = 1
      }
      else {
        if (x.value == checkPass) {
          checkPass = 1
        }
        else {
          isfalse = 1
          labelTC.innerHTML = "The password fields does NOT match!"
        }
      }
    })

    if (isfalse == 1) {
      labelTC.style.display = "block";
    }
    else {
      labelTC.style.display = "none";
      saveChanges.submit()
    }
  }


  /* _______Handles the content switch inside account page________ */
  const tabs = document.querySelectorAll("[data-tab-target]")
  const tabContents = document.querySelectorAll("[data-tab-content]")

  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      const target = document.querySelector(tab.dataset.tabTarget)
      tabContents.forEach(tabContents => {
        tabContents.classList.remove("show")
      })
      tabs.forEach(tab => {
        tab.classList.remove("show")
      })
      tab.classList.add("show")
      target.classList.add("show")
    })
  })



  




  /*___________________ LAYOUT _________________________*/
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

  //_________Submit button events after preventDefault__________
  $("a[name='goBtn']").click(function() {
    var text = $(this).text();

    if (text === "Market") {
      $("#goWallet").attr("action", "/market");
    }
    else if (text === "Wallet") {
      $("#goWallet").attr("action", "/wallet");
    }
    else if (text === "Account") {
      $("#goWallet").attr("action", "/account");
    }
    else if (text === "Logout") {
      $("#goWallet").attr("action", "/logout");
    }

    $("#goWallet").submit()
  })









  /*___________________ LOGIN _________________________*/

  const navbar = document.getElementById("navbar");
  const regBtn = document.getElementById("regBtn");

  navbar.style.visibility = "hidden";
  regBtn.style.visibility = "hidden";









/*___________________ MARKET _________________________*/


  function doEver(id) {
    let yAxis = {};
    let xAxis = {};

    getData(id);
  }

  /* _____________________ Gets data to build graph ___________________*/
  function getData(entry) {
    fetch("http://127.0.0.1:5000/getHistoricalData", {
      method: "POST",
      credentials: "include",
      body: JSON.stringify(entry),
      cache: "no-cache",
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

  /* _____________________ Builds Graph ___________________*/
  function doGraph(xData, yData, ticker) {
    var config = {
      type: 'line',
      data: {
        labels: xData,
        datasets: [{
          label: ticker,
          backgroundColor: "black",
          borderColor: "#17c3b2",
          data: yData,
          fill: false,
        }]
      },
      options: {
        responsive: true,
        title: {
          display: true,
          text: '5 YEAR PERFORMANCE: ' + ticker,
          fontFamily: "SuisseIntl-SemiBold,Helvetica,Arial,sans-serif",
          fontColor: "#00b4d8",
          fontSize: 18,
          lineHeight: 1.5
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
            ticks: {
              fontColor: "#a9def9"
            }
          }],
          yAxes: [{
            display: true,
            fontColor: "#17c3b2",
            ticks: {
              fontColor: "#a9def9"
            }
          }]
        },
        legend: {
          display: false
        }
      }

    };
    var ctx = document.getElementById('canvas').getContext('2d');
    window.myLine = new Chart(ctx, config);
  }

  function resetGraph() {
    document.getElementById("canvas").remove();

    var divG = document.getElementById("graph-container");
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

    if (mLabel.innerHTML === "Invalid ticker symbol!") {
      mLabel.innerHTML = "Cannot continue without a valid ticker symbol!"
      return null
    }

    document.getElementById("tickerInput").value = mModal.value;

    if (mModal.value === "") {
      mLabel.innerHTML = "You need to insert a ticket symbol to continue!"
    }
    else {
      event.preventDefault()
      if (modal.style.visibility === "hidden") {
        modal.style.visibility = "visible";
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

    if (id !== "noPad td-market") {
      if (mModal.value === "") {
        mLabel.innerHTML = "You need to insert a ticket symbol to continue!"
        mLabel.style.visibility = "visible";
        return;
      }
    }

    if (id === "noPad td-market") {
      ticker = ticknoPad;
    }
    else {
      ticker = document.getElementById("mModal").value;
    }

    // _____ If Process Order Button is pressed and exists quote data 
    if (mLabel.innerHTML === "notFirst") {
      companyName = document.getElementById("companyName").innerText;
      companyPrice = document.getElementById("companyPrice").innerText;

      both = companyPrice + "/" + companyName;

      document.getElementById("nameInput").value = both;
      document.getElementById("quoteTypeInput").value = document.getElementById("quoteType").innerText;

      document.getElementById("superLabel").innerText = "Current price of " + companyName + " is: " + companyPrice + ".";
      document.getElementById("labelYTD").innerText = "52 Week Change: " + document.getElementById("fifty2WC").innerText + "%.";
      return;
    }

    // ____ Gets quote data from the server
    fetch("http://127.0.0.1:5000/getPrice", {
      method: "POST",
      credentials: "include",
      body: JSON.stringify(ticker),
      cache: "no-cache",
      headers: new Headers({
        "content-type": "application/json"
      })
    })
      .then(response => response.json())
      .then(data => {

        if (data == "quote-error") {
          document.getElementById("mLabel").innerText = "Invalid ticker symbol!";
          mLabel.style.visibility = "visible";
        }
        else {

          if (id === "checkPriceBtn") { /* If check button is pressed */
            mLabel.style.visibility = "hidden";
            mLabel.innerHTML = "notFirst";

            document.getElementById("companyName").innerText = data["companyName"]
            document.getElementById("companyPrice").innerText = data["price"]
            document.getElementById("fifty2WC").innerText = data["fifty2WC"]
            document.getElementById("fifty2WL").innerText = data["fifty2WL"]
            document.getElementById("fifty2WH").innerText = data["fifty2WH"]
            document.getElementById("trailingPE").innerText = data["trailingPE"]
            document.getElementById("quoteType").innerText = data["quoteType"]

            document.getElementById("quoteInfoContainer").style.visibility = "visible"

          }
          else { /* If submit order button is pressed */

            both = data["price"] + "/" + data["companyName"];

            document.getElementById("nameInput").value = both;
            document.getElementById("quoteTypeInput").value = data["quoteType"];

            document.getElementById("superLabel").innerText = "Current price of " + data["companyName"] + " is: " + data["price"] + ".";
            document.getElementById("labelYTD").innerText = "52 Week Change: " + data["fifty2WC"] + "%.";

            alert(document.getElementById("nameInput").value);

          }
        }

      })
  }

  window.onload = function () {
    doEver("TSLA");
  }

  //_________________Hides pop up windows from load__________________
  let modal = document.getElementById("bgmodal");
  modal.style.visibility = "hidden";

  //_____Closes the POPUP window and resets buy/sell btn toggle_____
  function miniToggleModal() {
    modal.style.visibility = "hidden";
    document.getElementById("btnSell").className = "default-button button-changes-popup";
    document.getElementById("btnBuy").className = "default-button button-changes-popup";
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
      toDesactive.className = "default-button button-changes-popup";
    }
  }

  //____________Handles buy/sell buttons on click _____
  $(document).click(function (e) {
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















  /*___________________ REGISTER _________________________*/


  const navbar = document.getElementById("navbar");
  const regBtn = document.getElementById("regtn");

  navbar.style.visibility = "hidden";
  regBtn.style.visibility = "hidden";










  /*___________________ WALLET _________________________*/
  

	window.onload = function () {
		buildPieChart()
	}

	/*________ Handles alert messagem when buying assets ________*/
	function hideAlarmContainer() {
		const alarmContainer = document.getElementById("alarmContainer");
		if (alarmContainer !== null) {
			alarmContainer.style.display = "none";
		}
	}
	setTimeout(hideAlarmContainer, 3000);


	/*_________ Gets asset info and loads asset info box _________*/
	function getAssetData(e) {
		ticker = e.innerHTML;

		fetch("http://127.0.0.1:5000/getPrice", {
			method: "POST",
			credentials: "include",
			body: JSON.stringify(ticker),
			cache: "no-cache",
			headers: new Headers({
				"content-type": "application/json"
			})
		})
			.then(response => response.json())
			.then(data => {

				price = data["price"];
				ytdChange = data["ytdChange"]
				companyName = data["companyName"]

				document.getElementById("labelTickerSymbol").innerText = ticker;
				document.getElementById("labelCompanyName").innerText = companyName;
				document.getElementById("labelCurrentPrice").innerText = "$ " + price;
				document.getElementById("labelYearDate").innerText = ytdChange + " %";

			})
	}


	/* ___________ GETS DATA AND BUILDS PIE CHART _____________*/
	function buildPieChart() {

		/* _____ GETS DATA _____*/
		fetch("http://127.0.0.1:5000/getAssetAloc", {
			method: "GET"
		})
			.then(response => response.json())
			.then(data => {
				let label = []
				let dataset = []

				const colors = ["#81b29a", "#2a9d8f", "#457b9d", "#1d3557", "#14213d", "#dee2ff", "#cbc0d3", "#64653", "#6b705c", "#d4a373"];

				data.forEach(x => {
					label.push(x[0]);
					dataset.push(x[1]);
				})

				/* _____ BUILDS PIE CHART _____*/
				var ctx = document.getElementById('canvas').getContext('2d');
				var myPieChart = new Chart(ctx, {
					type: 'pie',
					data: {
						labels: label,
						datasets: [{
							data: dataset,
							backgroundColor: colors,
							borderColor: "lightgray"
						}]
					},
					options: {
						responsive: true,
						legend: {
							position: "right",
							labels: {
								fontSize: 9,
								fontColor: "#17c3b2"
							}
						}
					}
				})
			})
	}
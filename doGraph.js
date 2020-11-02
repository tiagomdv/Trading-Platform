     
  function getData(entry) {
    fetch("http://127.0.0.1:5000/fetchDo", {
      method: "POST",
      credentials: "include",
      body: JSON.stringify(entry),
      cache:"no-cache",
      headers: new Headers({
      "content-type": "application/json"
      })
    })
    .then(response => response.json())
    .then(result => console.log(result))
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
					text: 'Chart.js Line Chart'
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

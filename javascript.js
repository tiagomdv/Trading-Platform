$(function() {
  $('a#calculate').bind('click', function() {
    location.reload();
  });
});

// POST REQUEST

fetch(url, {
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

// GET REQUEST

fetch(url)
.then(function (response) {
return response.text();
}).then(function (text) {
console.log("GET response text:");
console.log(text);
});

// USING ASYNC FUNCTION

var entry = ["COCO", "XIXI", "TROTRO"]
var url = "http://127.0.0.1:5000/fetchDo"

let response = await fetch(url);

let result = response.json();

console.log(result)
console.log(result.message)
alert(result.message)


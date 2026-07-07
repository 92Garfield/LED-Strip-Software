function httpPost(url, data, callback) {
    let xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            callback(this.responseText);
        }
    };

    let dataArr = [];
    for (let key in data) {
        dataArr.push(key + "=" + data[key]);
    }

    xhttp.open("POST", url, true);
    xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");

    xhttp.send(dataArr.join("&"));
}

window.addEventListener('load', init);
function init() {
    console.log("Hello World");

    let doc = document.getElementById("app");
    let htmlInterface = new HTMLInterface();

    doc.appendChild(htmlInterface);
}
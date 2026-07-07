class HTMLInterface extends HTMLElement {
    constructor() {
        super();

        //heading
        let heading = document.createElement("h1");
        heading.innerHTML = "Testing";
        this.appendChild(heading);

        this.appendChild(document.createElement("br"));
        this.appendChild(document.createElement("br"));

        //data input
        let input = document.createElement("input");
        input.type = "text";
        input.placeholder = "";
        this.appendChild(input);

        //buttons
        let button = document.createElement("input");
        button.type = "button";
        button.value = "Test 1";
        button.addEventListener("click", function() {
            this._sendData({
                "type": "set",
                "data": input.value
            });
        }.bind(this));
        this.appendChild(button);

        this._style();
    }

    _style() {

    }

    _sendData(data) {
        httpPost("data", data, function(response) {
            console.log(response);
        });
    }
}

window.customElements.define('html-interface', HTMLInterface);
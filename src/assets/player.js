var canvas;
var socket;
var controls;

function resizeCanvas() {
    let canvas_h = canvas.clientHeight;
    let canvas_w = canvas.clientWidth;

    let width = 600;
    let height = width * canvas_h / canvas_w;

    canvas.setAttribute("viewBox", "0 0 " + width.toString() + " " + height.toString());
}

function modifyPaths(id, properties) {
    let p = document.getElementById(id);
    if (p == null) {
        p = document.createElementNS("http://www.w3.org/2000/svg", 'path');
        p.id = id;
        canvas.appendChild(p);
    }
    for (let prop in properties) {
        p.setAttribute(prop, properties[prop]);
    }
}

function sliderMove(event) {
    const msg = {'type': 'control',
                 'id': event.target.id,
                 'value': event.target.value};
    socket.send(JSON.stringify(msg));
}

function createControls(name, stroke, fill) {
    const temp = document.getElementById("ship-control-template");
    let c = temp.content.cloneNode(true);
    let divs = c.querySelectorAll("div");
    divs[0].style.border = "solid " + stroke;
    divs[0].style.backgroundColor = fill;
    let a = c.querySelectorAll("input");
    a[0].id = name + ".thrust";
    a[1].id = name + ".steer";
    a[0].oninput = sliderMove;
    a[1].oninput = sliderMove;
    let title = c.querySelectorAll("h5")[0];
    title.textContent = name;
    controls.appendChild(c);
}

document.addEventListener('DOMContentLoaded', (event) => {
    canvas = document.getElementById('canvas');
    controls = document.getElementById('ship-control-div');
    button = document.getElementById('go-btn');
    button.addEventListener("click", (event) => {
        const msg = {'type': 'go'};
        socket.send(JSON.stringify(msg));
    })
    resizeCanvas();

    socket = new WebSocket("ws://" + location.hostname + ":8080");
    socket.addEventListener("message", (event) => {
        const msg = JSON.parse(event.data);
        switch (msg.type) {
            case "paths":
                for (let p in msg.paths) {
                    modifyPaths(p, msg.paths[p]);
                }
            break;

            case "create-controls":
                for (let s of msg.controls) {
                    createControls(s.name, s.stroke, s.fill)
                }
            break;

            case "modify-controls":
                for (let ship in msg.controls) {
                    let st = document.getElementById(ship + '.steer');
                    let th = document.getElementById(ship + '.thrust');
                    st.value = msg.controls[ship]['steer'];
                    th.value = msg.controls[ship]['thrust'];
                }
            break;

            default:
                console.log("Invalid message type", msg);

        }
    });

});

window.addEventListener('resize', resizeCanvas);
var canvas;
var socket;
var controls;
var page_type;

function resizeCanvas() {
    let canvas_h = canvas.clientHeight;
    let canvas_w = canvas.clientWidth;

    let width = 900;
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

function drawGridLine(start, end) {
    p = document.createElementNS("http://www.w3.org/2000/svg", 'path');
    canvas.appendChild(p);
    p.setAttribute('d', 'M ' + start[0] + ',' + start[1] + ' L ' + end[0] + ',' + end[1]);
    p.setAttribute('stroke', 'LightCyan');
    p.setAttribute('fill', 'none');
}

function controlChange(event) {
    const msg = {'type': page_type,
                 'id': event.target.id,
                 'value': event.target.value};
    socket.send(JSON.stringify(msg));
}


function sendOverride(event) {
    name = event.target.id.split('.')[0];
    posX = document.getElementById(name + '.posX');
    posY = document.getElementById(name + '.posY');
    rot = document.getElementById(name + '.rot');
    enabled = document.getElementById(name + '.enable');
    const msg = {
        'type': 'override',
        'ship': name,
        'pos': [posX, posY],
        'rot': rot,
        'enabled': enabled,
    }
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
    a[2].id = name + ".roll";
    a[0].oninput = controlChange;
    a[1].oninput = controlChange;
    a[2].oninput = controlChange;
    let title = c.querySelectorAll("h5")[0];
    title.textContent = name;
    let ac = c.getElementById("ac");
    let speed = c.getElementById("speed");
    ac.id = name + ".ac";
    speed.id = name + ".speed";
    controls.appendChild(c);
}

function createGMControls(name, stroke, fill) {
    const temp = document.getElementById("gm-control-template");
    let c = temp.content.cloneNode(true);
    let divs = c.querySelectorAll("div");
    divs[0].style.border = "solid " + stroke;
    divs[0].style.backgroundColor = fill;
    let a = c.querySelectorAll("input");
    a[0].id = name + ".posX";
    a[1].id = name + ".posY";
    a[2].id = name + ".rot";
    a[3].id = name + ".enable";
    let title = c.querySelectorAll("h5")[0];
    title.textContent = name;
    a[4].id = name + ".submit";
    a[4].onclick = sendOverride;
    controls.appendChild(c);
}


function createGrid() {
    let w = canvas.getAttribute("viewBox").split(' ')[2];
    let h = canvas.getAttribute("viewBox").split(' ')[3];
    let step = 20;
    for (i = step; i < w; i += step) {
        drawGridLine([i, 0], [i, h]);
    }
    for (i = step; i < h; i += step) {
        drawGridLine([0, i], [w, i]);
    }
}


function wsHandler(event) {
    const msg = JSON.parse(event.data);
    switch (msg.type) {
        case "state":
            for (let p in msg.paths) {
                modifyPaths(p, msg.paths[p]);
            }

            for (let s in msg.status) {
                let ac = document.getElementById(s + '.ac');
                let speed = document.getElementById(s + '.speed');
                if ((ac != null) && (speed != null)) {
                    ac.textContent = msg.status[s]['ac'];
                    speed.textContent = msg.status[s]['speed'];
                }
            }
        break;

        case "create-controls":
            if (page_type == "player") {
                for (let s of msg.players) {
                    createControls(s.name, s.stroke, s.fill);
                }
            } else if (page_type == "gm") {
                for (let s of msg.enemies) {
                    createControls(s.name, s.stroke, s.fill);
                }
                for (let s of msg.players) {
                    createGMControls(s.name, s.stroke, s.fill);
                }
            } else {
                console.log("Invalid control type", msg);
            }

        break;

        case "modify-controls":
            for (let ship in msg.controls) {
                let st = document.getElementById(ship + '.steer');
                let th = document.getElementById(ship + '.thrust');
                let rl = document.getElementById(ship + '.roll');
                if (st != null)
                    st.value = msg.controls[ship]['steer'];
                if (th != null)
                    th.value = msg.controls[ship]['thrust'];
                if (rl != null)
                    rl.value = msg.controls[ship]['roll'];
            }
        break;

        default:
            console.log("Invalid message type", msg);

    }
}
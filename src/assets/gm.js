
function dragPosition(event) {
    if (clicked_ship != null) {
        let name = clicked_ship.split('.')[0];
        var pt = canvas.createSVGPoint();
        pt.x = event.clientX;
        pt.y = event.clientY;
        var pt_global = pt.matrixTransform(canvas.getScreenCTM().inverse());
        const msg = {
            'type': 'override',
            'page': page_type,
            'ship': name,
            'pos': [pt_global.x, pt_global.y],
            'rot': '',
            'enabled': 1,
        };
        socket.send(JSON.stringify(msg));
    }
}

document.addEventListener('DOMContentLoaded', (event) => {
    canvas = document.getElementById('canvas');
    controls = document.getElementById('ship-control-div');
    button = document.getElementById('go-btn');
    page_type = "gm";
    button.addEventListener("click", () => {
        const msg = {'type': 'go'};
        socket.send(JSON.stringify(msg));
    })
    resizeCanvas();
    createGrid();

    socket = new WebSocket("ws://" + location.hostname + ":8080");
    socket.addEventListener("message", wsHandler);

    canvas.addEventListener("mouseup", (event) => {
        clicked_ship = null;
    })

    canvas.onmousemove = dragPosition;
});

window.addEventListener('resize', resizeCanvas);
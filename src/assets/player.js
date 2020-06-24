
document.addEventListener('DOMContentLoaded', (event) => {
    canvas = document.getElementById('canvas');
    controls = document.getElementById('ship-control-div');
    button = document.getElementById('go-btn');
    page_type = "player";
    resizeCanvas();
    createGrid();

    socket = new WebSocket("ws://" + location.hostname + ":8080");
    socket.addEventListener("message", wsHandler);
});

window.addEventListener('resize', resizeCanvas);
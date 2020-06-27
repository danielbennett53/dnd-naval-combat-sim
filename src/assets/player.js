
document.addEventListener('DOMContentLoaded', (event) => {
    canvas = document.getElementById('canvas');
    controls = document.getElementById('ship-control-div');
    button = document.getElementById('go-btn');
    const show_weapons = document.getElementById('show-enemy-weapons');

    page_type = "player";
    resizeCanvas();
    createGrid();

    socket = new WebSocket("ws://" + location.hostname + ":8080");
    socket.addEventListener("message", wsHandler);

    show_weapons.addEventListener("change", (event) => {
        const paths = document.querySelectorAll("path");
        for (let p of paths) {
            if (p.id.includes('weapon') && p.id.includes('enemy')) {
                if (event.target.checked) {
                    p.style.visibility = 'visible';
                } else {
                    p.style.visibility = 'hidden';
                }
            }
        }
    })
});

window.addEventListener('resize', resizeCanvas);
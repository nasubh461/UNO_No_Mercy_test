document.addEventListener("DOMContentLoaded", function () {
    var socket = io();
    var roomCode = window.roomCode;
    var playerList = document.getElementById("player-list");
    var leaveButton = document.getElementById("leave-room-btn");

    // Retrieve username from localStorage
    var sessionToken = localStorage.getItem("session_token");

    // Redirect to home page if session token is missing
    if (!sessionToken) {
        alert("Session expired or missing. Please rejoin the room.");
        window.location.href = "/";
        return;
    }

    function updatePlayerList(players) {
        playerList.innerHTML = "";
        players.forEach(player => {
            let li = document.createElement("li");
            li.textContent = player;
            playerList.appendChild(li);
        });
    }

    // Fetch username from session token
    fetch('/get_username', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_token: sessionToken })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            let username = data.username;

            // Emit event with username
            socket.emit("join_room", { room: roomCode, username: username, session: sessionToken });

            socket.on("update_players", function (data) {
                updatePlayerList(data.players);
            });

            leaveButton.addEventListener("click", function () {
                socket.emit("leave_room", { room: roomCode, username: username, session: sessionToken });
                localStorage.removeItem("session_token");
                window.location.href = "/";
            });
        } else {
            alert("Session invalid. Please rejoin the room.");
            localStorage.removeItem("session_token");
            window.location.href = "/";
        }
    })
    .catch(error => console.error('Error verifying session:', error));
});

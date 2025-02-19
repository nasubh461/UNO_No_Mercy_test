document.addEventListener("DOMContentLoaded", function () {
    var socket = io();
    var roomCode = window.roomCode;
    var playerList = document.getElementById("player-list");
    var leaveButton = document.getElementById("leave-room-btn");
    var startGameButton = document.getElementById("start-game-btn");

    // Retrieve username from localStorage
    var sessionToken = localStorage.getItem("session_token");

    if (!sessionToken) {
        alert("Session expired or missing. Please rejoin the room.");
        window.location.href = "/";
        return;
    }

    function updatePlayerList(players) {
        playerList.innerHTML = "";
        players.forEach((player, index) => {
            let li = document.createElement("li");
            li.textContent = player;
            playerList.appendChild(li);

            // Show "Start Game" button only for the first player
            if (index === 0 && player === localStorage.getItem("username")) {
                startGameButton.style.display = "block";
            }
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
            localStorage.setItem("username", username);

            // Emit event to join room
            socket.emit("join_room", { room: roomCode, username: username, session: sessionToken });

            socket.on("update_players", function (data) {
                updatePlayerList(data.players);
            });

            socket.on("game_started", function () {
                alert("Game has started! No new players can join.");
                startGameButton.style.display = "none"; // Hide start button
                
            });

            socket.on("your_hand", function (data) {
                console.log("Your Hand:", data.hand);
            });

            leaveButton.addEventListener("click", function () {
                socket.emit("leave_room", { room: roomCode, username: username, session: sessionToken });
                localStorage.removeItem("session_token");
                localStorage.removeItem("username");
                window.location.href = "/";
            });

            startGameButton.addEventListener("click", function () {
                fetch('/start_game', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ room_code: roomCode, username: username })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === "started") {
                        alert("Game started!");
                        socket.emit("game_started", { room: roomCode });
                    } else if (data.status === "not_enough_players") {
                        alert("At least 2 players are required to start the game.");
                    } else {
                        alert("You are not authorized to start the game.");
                    }
                });
            });

        } else {
            alert("Session invalid. Please rejoin the room.");
            localStorage.removeItem("session_token");
            window.location.href = "/";
        }
    })
    .catch(error => console.error('Error verifying session:', error));
});

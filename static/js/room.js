document.addEventListener("DOMContentLoaded", function () {
    var socket = io();
    var roomCode = window.roomCode;
    var playerList = document.getElementById("player-list");
    var leaveButton = document.getElementById("leave-room-btn");
    var startGameButton = document.getElementById("start-game-btn");
    var drawButton = document.getElementById("draw-card-btn");
    var newGameButton = document.getElementById("new-game-btn");


    let currentHand = [];

    // Retrieve username from localStorage
    var sessionToken = localStorage.getItem("session_token");

    if (!sessionToken) {
        alert("Session expired or missing. Please rejoin the room.");
        window.location.href = "/";
        return;
    }

    drawButton.addEventListener("click", function() {
        socket.emit("draw_card", { room: roomCode });
    });

    // Add click handler for new game button
    newGameButton.addEventListener("click", function() {
        socket.emit("leave_room", { 
            room: roomCode, 
            username: localStorage.getItem("username"), 
            session: sessionToken 
        });
        localStorage.removeItem("session_token");
        localStorage.removeItem("username");
        window.location.href = "/";
    });

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

    function getCardColor(color) {
        const colors = {
            'Red': '#ff0000',
            'Blue': '#0000ff',
            'Green': '#00ff00',
            'Yellow': '#ffff00',
            'Wild': '#808080'
        };
        return colors[color] || '#ffffff';
    }
    
    function updateHandDisplay() {
        const container = document.getElementById('hand-container');
        container.innerHTML = '';
        currentHand.forEach((card, index) => {
            const cardBtn = document.createElement('button');
            cardBtn.className = 'card';
            cardBtn.style.backgroundColor = getCardColor(card.color);
            cardBtn.innerHTML = `
                <div class="card-top">${card.color}</div>
                <div class="card-center">${card.type || card.value}</div>
            `;
            cardBtn.dataset.index = index;
            
            // Add different style for wild cards
            if (card.color === 'Wild') {
                cardBtn.classList.add('wild-card');
                cardBtn.style.color = 'white';
            }
            
            cardBtn.addEventListener('click', () => handlePlayCard(index, card));
            container.appendChild(cardBtn);
        });
    }

    async function handlePlayCard(index, card) {
        if (card.color === 'Wild' && card.type !== 'Color Roulette') {
            const color = await promptColor();
            if (!color) return;
            socket.emit('play_card', {
                room: roomCode,
                index: index,
                color: color
            });
        } else {
            socket.emit('play_card', {
                room: roomCode,
                index: index
            });
        }
    }
    
    function promptColor() {
        return new Promise(resolve => {
            const colorPicker = document.createElement('div');
            colorPicker.innerHTML = `
                <div style="position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; padding: 20px;">
                    <p>Choose a color:</p>
                    <button style="background: red; padding: 10px;" data-color="Red"></button>
                    <button style="background: blue; padding: 10px;" data-color="Blue"></button>
                    <button style="background: green; padding: 10px;" data-color="Green"></button>
                    <button style="background: yellow; padding: 10px;" data-color="Yellow"></button>
                </div>
            `;
            
            document.body.appendChild(colorPicker);
            
            colorPicker.querySelectorAll('button').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    document.body.removeChild(colorPicker);
                    resolve(e.target.dataset.color);
                });
            });
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
            
            socket.on("game_started", function (data) {
                console.log("=== GAME STARTED ===");
                console.log("Initial Discard:", data.discard_top);
                console.log("Cards Remaining:", data.cards_left);
                console.log("====================");      
                
                alert("Game has started! No new players can join.");
                updatePlayerList(data.shuffled_players);
                startGameButton.style.display = "none";
            });

            socket.on("your_hand", function (data) {
                console.log("=== YOUR HAND ===");
                console.log("Cards:", data.hand);
                console.log("Discard Pile Top:", data.discard_top);
                console.log("Cards Left in Deck:", data.cards_left);
                console.log("==================");

                currentHand = data.hand;
                updateHandDisplay();
                
                document.getElementById('discard-top').textContent = `${data.discard_top.color} ${data.discard_top.type || data.discard_top.value}`;
            });

            // Add new event listener for game state updates
            socket.on("game_update", function(data) {
                document.getElementById('current-turn').textContent = `Current turn: ${data.current_player}`;
                document.getElementById('discard-top').textContent = `${data.discard_top.color} ${data.discard_top.type || data.discard_top.value}`;

                // Get current user from localStorage
                const currentUser = localStorage.getItem("username");
                
                // Show draw button only for current player
                if (data.current_player === currentUser) {
                    drawButton.style.display = "block";
                } else {
                    drawButton.style.display = "none";
                }
            });

            socket.on("play_error", function(data) {
                alert(data.message);
            });

            socket.on("player_disqualified", function(data) {
                alert(data.player + " is eleminated");
            });

            socket.on("roulette", async function() {
                console.log("=== SPIN ROULETTE ===");
                try {
                    const color = await promptColor();
                    socket.emit("color_selected", { 
                        room: roomCode,
                        color: color
                    });
                } catch (error) {
                    console.error("Color selection failed:", error);
                }
            });

            socket.on("card_drawn", function (data) {
                console.log("=== CARD DRAWN ===");
                console.log("Player:", data.player);
                console.log("New Card:", data.new_card);
                console.log("Remaining Cards:", data.cards_left);
                console.log("==================");

                // Add new cards to current hand
                currentHand.push(data.new_card);
                updateHandDisplay();
                
                // Enable play button if valid moves exist
                playButton.style.display = "block";
            });

            socket.on("room_deleted", function (data) {
                console.log("Room deleted event received:", data);
                alert(data.message);
                window.location.href = "/";
            });
            
            socket.on("roulette_draw", function (data) {
                console.log("Roulette Card Drawn")
                console.log(data.card_drawn)

            });

            socket.on("roulette_end", function () {
                alert("Roulette ended choosen color found")
            });

            socket.on("game_over", function (data) {
                document.getElementById('discard-top').textContent = `${data.discard_top.color} ${data.discard_top.type || data.discard_top.value}`;
                // Hide game controls
                drawButton.style.display = 'none';
                leaveButton.style.display = 'none';
                // Show new game button
                newGameButton.style.display = 'block';
                alert(data.winner + " has won the game!");
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
document.getElementById('create-room-btn').addEventListener('click', function() {
    document.getElementById('create-room-modal').style.display = 'block';
});

document.getElementById('join-room-btn').addEventListener('click', function() {
    document.getElementById('join-room-modal').style.display = 'block';
});

document.getElementById('close-create-room').addEventListener('click', function() {
    document.getElementById('create-room-modal').style.display = 'none';
});

document.getElementById('close-join-room').addEventListener('click', function() {
    document.getElementById('join-room-modal').style.display = 'none';
});

document.getElementById('create-room-submit').addEventListener('click', function() {
    let playerName = document.getElementById('create-player-name').value;
    if (playerName) {
        fetch('/create_room', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                let roomCode = data.room_code;
                alert("Room created! Your room code is: " + roomCode);
                window.location.href = "/room/" + roomCode; // Redirect to the room page
            })
            .catch(error => console.error('Error creating room:', error));
    }
});


document.getElementById('join-room-submit').addEventListener('click', function() {
    let playerName = document.getElementById('join-player-name').value;
    let roomCode = document.getElementById('join-room-code').value;
    if (playerName && roomCode) {
        // Simulate joining room
        alert("Joining room with code: " + roomCode);
        // Redirect to room page
        window.location.href = "/room/" + roomCode;
        document.getElementById('join-room-modal').style.display = 'none';
    }
});

// Close modals when clicking outside of them
window.onclick = function(event) {
    let createModal = document.getElementById('create-room-modal');
    let joinModal = document.getElementById('join-room-modal');
    if (event.target == createModal) {
        createModal.style.display = 'none';
    }
    if (event.target == joinModal) {
        joinModal.style.display = 'none';
    }
}
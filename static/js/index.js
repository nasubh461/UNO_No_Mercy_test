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
    let playerName = document.getElementById('create-player-name').value.trim();

    if (!playerName || /^\d+$/.test(playerName)) {
        alert("Username must contain at least one letter and cannot be empty.");
        return;
    }

    fetch('/create_room', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: playerName })
    })
    .then(response => response.json())
    .then(data => {
        localStorage.setItem('session_token', data.session_token);
        window.location.href = `/room/${data.room_code}`;
    })
    .catch(error => console.error('Error creating room:', error));
});

document.getElementById('join-room-submit').addEventListener('click', function() {
    let playerName = document.getElementById('join-player-name').value.trim();
    let roomCode = document.getElementById('join-room-code').value.trim().toUpperCase();

    if (!playerName || /^\d+$/.test(playerName)) {
        alert("Username must contain at least one letter and cannot be empty.");
        return;
    }

    if (!roomCode) {
        alert("Room code cannot be empty.");
        return;
    }

    fetch('/join_room', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: playerName, room_code: roomCode })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'joined') {
            localStorage.setItem('session_token', data.session_token);
            window.location.href = `/room/${roomCode}`;
        } else if (data.status === 'duplicate') {
            alert("Username already exists in the room. Please choose another name.");
        } else {
            alert("Room not found.");
        }
    })
    .catch(error => console.error('Error joining room:', error));
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
};

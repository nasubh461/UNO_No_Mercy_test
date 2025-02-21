document.getElementById('createRoom').addEventListener('click', function() {
    // Redirect to templates/createRoom.html
    window.location.href = '/createRoom';
});


// Create Room
document.getElementById('createRoomBtn').addEventListener('click', function () {
    const playerName = document.getElementById('playerName').value;

    if (!playerName) {
        alert('Please enter your name!');
        return;
    }

    fetch('/create-room', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ playerName: playerName })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('roomCodeDisplay').innerText = 'Room Code: ' + data.roomCode;
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('roomCodeDisplay').innerText = 'Failed to create room.';
    });
});
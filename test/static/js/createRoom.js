// Create Room
document.getElementById('createRoomBtn').addEventListener('click', function () {
    const playerName = document.getElementById('playerName').value;

    if (!playerName) {
        alert('Please enter your name!');
        return;
    }
    console.log("Button clicked");

    fetch('/create_room', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username: playerName })
    })
    .then(response => response.json())
    .then(data => {
        if (data.room_code) {
            document.getElementById('roomCodeDisplay').innerText = 'Room Code: ' + data.room_code;
            localStorage.setItem("session_token", data.session_token);
        } else {
            document.getElementById('roomCodeDisplay').innerText = 'Failed to create room.';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('roomCodeDisplay').innerText = 'Failed to create room.';
    });
});
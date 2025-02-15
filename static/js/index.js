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
        // Simulate API call to create room and get room code
        let roomCode = "123456"; // Replace with actual API call
        alert("Room created! Your room code is: " + roomCode);
        document.getElementById('create-room-modal').style.display = 'none';
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
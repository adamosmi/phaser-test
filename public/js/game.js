var config = {
    type: Phaser.AUTO,
    width: 800,
    height: 600,
    physics: {
        default: 'arcade',
        arcade: {
            gravity: { y: 300 },
            debug: false
        }
    },
    scene: {
        preload: preload,
        create: create,
        update: update
    }
};

var game = new Phaser.Game(config);
var websocket;

function preload() {
    // Preload assets
}

function create() {
    // Initialize your game scene
    websocket = new WebSocket('ws://52.151.251.63');

    websocket.onopen = function(event) {
        console.log('Connection established');
        // Send a test message to the server
        sendMessage('Hello from Phaser!');
    };

    websocket.onmessage = function(event) {
        console.log('Message from server: ', event.data);
    };

    websocket.onerror = function(event) {
        console.error('WebSocket error observed:', event);
    };
}

function update() {
    // Game update loop
}

// Function to send message to server
function sendMessage(message) {
    if (websocket.readyState === WebSocket.OPEN) {
        websocket.send(message);
        console.log('Message sent to server:', message);
    } else {
        console.error('WebSocket is not open.');
    }
}

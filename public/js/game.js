var config = {
    type: Phaser.AUTO,
    width: 800,
    height: 600,
    scene: {
        preload: preload,
        create: create,
        update: update
    }
};

var game = new Phaser.Game(config);
var websocket;
var gameState = {
    paddles: [{ y: 300 }, { y: 300 }],
    ball: { x: 400, y: 300 }
};

function preload() {
    // Preload assets, if you have any
}

function create() {
    // Initialize your game scene
    websocket = new WebSocket('ws://52.151.251.63');

    websocket.onopen = function(event) {
        console.log('Connection established');
        // Optionally, send a message to the server to indicate readiness
        sendMessage({ type: 'ready' });
    };

    websocket.onmessage = function(event) {
        // Parse the received message to update the game state
        gameState = JSON.parse(event.data);
    };

    websocket.onclose = function(event) {
        console.log('WebSocket is closed now.');
    };

    websocket.onerror = function(event) {
        console.error('WebSocket error observed:', event);
    };

    // Add two paddles as simple sprites or graphics
    this.paddle1 = this.add.rectangle(50, this.sys.game.config.height / 2, 10, 100, 0xffffff);
    this.paddle2 = this.add.rectangle(this.sys.game.config.width - 50, this.sys.game.config.height / 2, 10, 100, 0xffffff);

    // Add a ball as a simple sprite or graphic
    this.ball = this.add.circle(this.sys.game.config.width / 2, this.sys.game.config.height / 2, 7, 0xffffff);
    
    // Capture keyboard input
    this.cursors = this.input.keyboard.createCursorKeys();
}

function update() {
    // Check for user input and send paddle movements to the server
    if (this.cursors.up.isDown) {
        sendMessage({ type: 'move', direction: 'up' });
    } else if (this.cursors.down.isDown) {
        sendMessage({ type: 'move', direction: 'down' });
    }

    // Validate and update paddle and ball positions from the game state
    if (gameState && gameState.paddles && gameState.ball) {
        if (gameState.paddles[0] && gameState.paddles[1]) {
            this.paddle1.y = gameState.paddles[0].y;
            this.paddle2.y = gameState.paddles[1].y;
            this.ball.x = gameState.ball.x;
            this.ball.y = gameState.ball.y;
        }
    }
}


// Function to send message to server
function sendMessage(message) {
    if (websocket.readyState === WebSocket.OPEN) {
        websocket.send(JSON.stringify(message)); // Ensure you send a stringified JSON
        console.log('Message sent to server:', message);
    } else {
        console.error('WebSocket is not open.');
    }
}

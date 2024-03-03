import asyncio
import json
import websockets

# Assuming a 2-player game, for simplicity
players = {}
game_state = {
    "paddles": [{"y": 300}, {"y": 300}],
    "ball": {"x": 400, "y": 300},
}


async def game_loop():
    while True:
        # Here you would implement the logic to update the ball position
        # and check for collisions, scoring, etc.

        # After updating the state, broadcast it to each player
        state = json.dumps(game_state)
        for player in players.values():
            await player.send(state)
        await asyncio.sleep(1 / 60)  # Update at 60Hz


async def handler(websocket):
    global players, game_state
    # calc new player id
    num_players = len(players)
    # normal game of 2 players
    if num_players in [0, 1]:
        player_id = num_players

        # store connection
        players[player_id] = websocket

        # establish initial game state
        game_state["paddles"][player_id] = {"y": 300}

        try:
            async for message in websocket:
                # Process incoming messages, e.g., paddle movements
                data = json.loads(message)
                print(f"Received data: {data}")

                # Handle different types of events
                # Update paddle position based on input
                if data["type"] == "move":
                    # Placeholder logic; you will need to check for valid movement here
                    if data["direction"] == "up":
                        game_state["paddles"][player_id]["y"] -= 10
                    elif data["direction"] == "down":
                        game_state["paddles"][player_id]["y"] += 10

                # Handle player ready state
                elif data["type"] == "ready":
                    start_game_message = json.dumps(
                        {"type": "start", "player_id": player_id}
                    )
                    for player in players.values():
                        await player.send(start_game_message)

        except websockets.exceptions.ConnectionClosed:
            print(f"Player {player_id} connection closed")

        finally:
            del players[player_id]
            del game_state["paddles"][player_id]

    else:
        # add logic to handle more than 2 players
        pass


async def main():
    async with websockets.serve(handler, "", 8765):
        await asyncio.Future()  # run forever


async def host():
    tasks = [main(), game_loop()]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(host())

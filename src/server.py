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
        game_state_out = {"type": "state", "data": game_state}
        state = json.dumps(game_state_out)
        print(f"Sending state: {state}")
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
                data["player_id"] = player_id
                print(f"Received data: {data}")

                # Handle different types of events
                # Update paddle position based on input
                if data["type"] == "move":
                    # Placeholder logic; you will need to check for valid movement here
                    player_paddle_y = game_state["paddles"][player_id]["y"]
                    player_key_direction = data["direction"]

                    player_upper_limit = 0 + 50
                    player_lower_limit = 600 - 50

                    # test upper limit (0 on screen)
                    is_below_upper_limit = (
                        (player_paddle_y - 10) >= player_upper_limit
                    )  # losing 10 each frame as it approaches 0 (screen top)

                    # test lower limit (600 on screen)
                    is_above_lower_limit = (
                        (player_paddle_y + 10) <= player_lower_limit
                    )  # gaining 10 each frame as it approaches 600 (screen bottom)

                    if is_below_upper_limit and is_above_lower_limit:
                        if player_key_direction == "up":
                            game_state["paddles"][player_id]["y"] = player_paddle_y - 10
                        elif player_key_direction == "down":
                            game_state["paddles"][player_id]["y"] = player_paddle_y + 10

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
            # set value back to default on disconnect
            game_state["paddles"][player_id] = {"y": 300}

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

import asyncio
import json
import random
import websockets

# Assuming a 2-player game, for simplicity
players = {}
game_state = {
    "paddles": [{"y": 300}, {"y": 300}],
    "ball": {"x": 400, "y": 300},
    "scores": [0, 0],
}

# screen dimensions
screen_width = 800
screen_height = 600

# object dimensions
paddle_length = 100
paddle_width = 10
ball_radius = 7

# paddle position
init_paddle1_pos_x = 0 + 50
init_paddle2_pos_x = screen_width - 50

# paddle movement
VELOCITY = 10
paddle_velocity = {"y": VELOCITY}

# ball movement
ball_sign_x = random.choice([-1, 1])
ball_sign_y = random.choice([-1, 1])
ball_velocity = {"x": int(VELOCITY * 0.75), "y": int(VELOCITY * 0.75)}


def calculate_ball_position():
    global game_state, ball_sign_x, ball_sign_y
    ball_pos = game_state["ball"]
    ball_pos_x = ball_pos["x"]
    ball_pos_y = ball_pos["y"]

    # detect collision
    # collect paddle position
    paddle1_pos = game_state["paddles"][0]
    paddle2_pos = game_state["paddles"][1]
    paddle1_pos_y = paddle1_pos["y"]
    paddle2_pos_y = paddle2_pos["y"]

    # calculate paddle borders
    paddle1_box = {
        "x": {
            "min": init_paddle1_pos_x - paddle_width / 2,
            "max": init_paddle1_pos_x + paddle_width / 2,
        },
        "y": {
            "min": paddle1_pos_y - paddle_length / 2,
            "max": paddle1_pos_y + paddle_length / 2,
        },
    }
    paddle2_box = {
        "x": {
            "min": init_paddle2_pos_x - paddle_width / 2,
            "max": init_paddle2_pos_x + paddle_width / 2,
        },
        "y": {
            "min": paddle2_pos_y - paddle_length / 2,
            "max": paddle2_pos_y + paddle_length / 2,
        },
    }

    # calculate ball borders
    ball_box = {
        "x": {"min": ball_pos_x - ball_radius, "max": ball_pos_x + ball_radius},
        "y": {"min": ball_pos_y - ball_radius, "max": ball_pos_y + ball_radius},
    }

    # determine ball direction
    # test if position is past either box on the x axis (left of paddle1's rightmost edge, right of paddle2's leftmost edge)
    if (ball_box["x"]["min"] < paddle1_box["x"]["max"]) or (
        ball_box["x"]["max"] > paddle2_box["x"]["min"]
    ):
        # check to see if the ball is between the paddles
        if (
            # ball is between the y box of paddle1
            (ball_box["y"]["min"] > paddle1_box["y"]["min"])
            and (ball_box["y"]["max"] < paddle1_box["y"]["max"])
        ) or (
            # ball is between the y box of paddle2
            (ball_box["y"]["min"] > paddle2_box["y"]["min"])
            and (ball_box["y"]["max"] < paddle2_box["y"]["max"])
        ):
            print(f"Ball box: {ball_box}")
            print(f"Paddle1: {paddle1_box}")
            print(f"Paddle2: {paddle2_box}")
            ball_sign_x *= -1  # switch the balls direction

    # test if position is past the top or bottom of the screen
    if (ball_box["y"]["min"] < 0) or (ball_box["y"]["max"] > screen_height):
        print(f"Ball box: {ball_box}")
        ball_sign_y *= -1  # switch the balls direction

    # add score & reset ball
    if ball_box["x"]["min"] < 0:
        paddle1_score = game_state["scores"][0]
        game_state["scores"][0] = paddle1_score + 1
        return {"x": 400, "y": 300}

    elif ball_box["x"]["max"] > screen_width:
        paddle2_score = game_state["scores"][1]
        game_state["scores"][1] = paddle2_score + 1
        return {"x": 400, "y": 300}

    # update ball position
    else:
        return {
            "x": ball_pos_x + ball_velocity["x"] * ball_sign_x,
            # "x": ball_pos_x + 1,
            "y": ball_pos_y + ball_velocity["y"] * ball_sign_y,
            # "y": ball_pos_y + 1,
        }


# define game loop
async def game_loop():
    while True:
        # Here you would implement the logic to update the ball position
        # and check for collisions, scoring, etc.
        game_state["ball"] = calculate_ball_position()

        # After updating the state, broadcast it to each player
        game_state_out = {"type": "state", "data": game_state}
        state = json.dumps(game_state_out)
        print(f"Sending state: {state}")
        for player in players.values():
            await player.send(state)
        await asyncio.sleep(1 / 60)  # Update at 60Hz


# define message handling logic
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

                    # bounds + paddle length / 2
                    player_upper_limit = 0 + paddle_length / 2
                    player_lower_limit = screen_height - paddle_length / 2

                    # move player towards upper limit
                    if (player_key_direction == "up") and (
                        player_paddle_y > player_upper_limit
                    ):
                        game_state["paddles"][player_id]["y"] = (
                            player_paddle_y - paddle_velocity["y"]
                        )  # losing 10 each frame as it approaches 600 (screen bottom)

                    # move player towards lower limit
                    elif (player_key_direction == "down") and (
                        player_paddle_y < player_lower_limit
                    ):
                        game_state["paddles"][player_id]["y"] = (
                            player_paddle_y + paddle_velocity["y"]
                        )  # gaining 10 each frame as it approaches 600 (screen bottom)

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


# run paddle logic
async def main():
    async with websockets.serve(handler, "", 8765):
        await asyncio.Future()  # run forever


async def host():
    tasks = [main(), game_loop()]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(host())

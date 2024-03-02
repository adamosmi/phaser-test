import asyncio
import websockets


async def main():
    async for websocket in websockets.connect("ws://52.151.251.63"):
        try:
            i = 0
            while True:
                await websocket.send(message=f"Sending message: {i}")
                i += 1
                await asyncio.sleep(1)
                print(f"Sending message: {i}")
        except websockets.ConnectionClosed:
            continue


if __name__ == "__main__":
    asyncio.run(main())

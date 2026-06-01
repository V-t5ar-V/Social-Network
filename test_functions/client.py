import asyncio
import websockets

async def main():
    port = "8000"
    ip = "127.0.0.1"
    url = f"ws://{ip}:{port}"
    try:
        async with websockets.connect(url) as websocket:
            message = input("enter message: ")

            await websocket.send(message)
            response = await websocket.recv()

            print(response)
    except ConnectionRefusedError:
        print('Connection refused')


asyncio.run(main())
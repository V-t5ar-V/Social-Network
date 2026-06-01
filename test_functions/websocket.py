import websockets
import asyncio

async def echo(websocket):
    async for message in websocket:
        print(message)

        response = f"Message \"{message}\" sent!"

        await websocket.send(response)

async def main():
    async with websockets.serve(echo, "127.0.0.1", 8080):

        print("server start")

        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
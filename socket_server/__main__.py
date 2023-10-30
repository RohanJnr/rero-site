import asyncio

from websockets.server import serve


async def tcp_echo_client(message):
    reader, writer = await asyncio.open_connection(
        '127.0.0.1', 12345)

    print(f'Send: {message!r}')
    writer.write(message.encode())
    await writer.drain()

    data = await reader.read(100)
    print(f'Received: {data.decode()!r}')

    print('Close the connection')
    writer.close()
    await writer.wait_closed()


async def callback(websocket):
    print("got connection.")
    print("Establishing connection with ESP server.")

    reader, writer = await asyncio.open_connection(
        '127.0.0.1', 12345
    )

    async for message in websocket:
        print(f"Got message: {message}")

        writer.write(message.encode())
        await writer.drain()
    
        await websocket.send("ECHO")
    
    print("closing connection.")
    writer.close()
    await writer.wait_closed()



async def main():
    async with serve(callback, "localhost", 9999):
        await asyncio.Future()

asyncio.run(main())
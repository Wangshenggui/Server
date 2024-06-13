import asyncio
import websockets
from websockets import ConnectionClosed
import json

connected_clients = []
websocket_connection = None
heartbeat_interval = 0.5  # 设置心跳包发送间隔为10秒

async def handle_client(reader, writer):
    addr = writer.get_extra_info('peername')
    print(f"客户端 {addr} 连接成功")

    connected_clients.append(writer)

    try:
        while True:
            data = await reader.read(100)
            if not data:
                break

            message = data.decode()
            print(f"收到来自客户端 {addr} 的消息: {message}")

            # 发送消息到 WebSocket 服务器
            await send_message_to_websocket(message)

            await writer.drain()
    except (ConnectionResetError, ConnectionError) as e:
        print(f"客户端 {addr} 连接错误: {e}")
    except Exception as e:
        print(f"处理客户端 {addr} 消息时发生错误: {e}")
    finally:
        if writer in connected_clients:
            connected_clients.remove(writer)
        print(f"客户端 {addr} 断开连接")
        writer.close()

async def broadcast_message_tcp(message):
    for client_writer in connected_clients:
        try:
            print(f"向 TCP 客户端发送消息: {message}")
            client_writer.write(message.encode())
            await client_writer.drain()
        except (ConnectionResetError, ConnectionError) as e:
            print(f"向 TCP 客户端发送消息时发生连接错误: {e}")
            if client_writer in connected_clients:
                connected_clients.remove(client_writer)
            client_writer.close()
        except Exception as e:
            print(f"向 TCP 客户端发送消息时发生错误: {e}")

async def send_message_to_websocket(message):
    if websocket_connection:
        try:
            print(f"发送消息到 WebSocket 服务器: {message}")
            await websocket_connection.send(message)
        except Exception as e:
            print(f"发送消息到 WebSocket 服务器时发生错误: {e}")

async def handle_websocket_message(message):
    print(f"收到来自 WebSocket 服务器的消息: {message}")
    try:
        json_message = json.loads(message)
        if "n1" in json_message or "lte" in json_message or "rtk" in json_message:
            await broadcast_message_tcp(message)
    except json.JSONDecodeError as e:
        print(f"解析 WebSocket 消息时发生错误: {e}")

async def websocket_client():
    global websocket_connection
    uri = "ws://8.137.81.229:8880"
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                websocket_connection = websocket
                while True:
                    message = await websocket.recv()
                    await handle_websocket_message(message)
        except (ConnectionClosed, ConnectionResetError, ConnectionError) as e:
            print(f"WebSocket 连接错误: {e}")
            websocket_connection = None
            await asyncio.sleep(5)  # 等待几秒钟再尝试重新连接

async def send_heartbeat():
    while True:
        await asyncio.sleep(heartbeat_interval)
        message = data.decode()
        print(f"发送心跳包: {message}")
        await broadcast_message_tcp(message)

async def main():
    server = await asyncio.start_server(
        handle_client, '172.29.103.118', 8881)

    addr = server.sockets[0].getsockname()
    print(f"服务器已启动，监听在 {addr}")

    asyncio.create_task(websocket_client())
    asyncio.create_task(send_heartbeat())

    async with server:
        await server.serve_forever()

asyncio.run(main())

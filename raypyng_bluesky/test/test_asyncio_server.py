from raypyng_bluesky.asyncio_server import ServerProtocol
import asyncio

loop = asyncio.get_event_loop()
tmp_folder = '/home/simone/Documents/RAYPYNG/raypyng_master/raypyng_bluesky/test/server_tmp'
try:
    server_coro = loop.create_server(lambda: ServerProtocol(tmp_folder), '127.0.0.1', 12345)
    server = loop.run_until_complete(server_coro)
except Exception as e:
    print('Error creating server:', e)
    
print("Server listening on", server.sockets[0].getsockname())

try:
    loop.run_forever()
except KeyboardInterrupt:
    pass
finally:
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()
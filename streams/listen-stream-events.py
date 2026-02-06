import asyncio
import json
import websockets

from common.auth import create_token

APS_CLIENT_ID = 'pErXeluFbvApeQYUoA7dnUoA6AoUsEv8'
APS_CLIENT_SECRET = 'CMslkMpATPJdJoSF'
FACILITY_URN = 'urn:adsk.dtt:WtMe53OeTWuvLaCP4bvZkw'

async def main():
    model_id = FACILITY_URN.replace('urn:adsk.dtt:', 'urn:adsk.dtm:')
    token = create_token(APS_CLIENT_ID, APS_CLIENT_SECRET, ['data:read'])
    async with websockets.connect('wss://tandem.autodesk.com/api/v1/msgws', additional_headers={'Authorization': f'Bearer {token}'}) as websocket:
        await websocket.send(f'/subscribe/{model_id}')
        async for message in websocket:
            message_obj = json.loads(message)
            print(message_obj)
        #response = await websocket.recv()
        #print(response)

if __name__ == '__main__':
    asyncio.run(main())
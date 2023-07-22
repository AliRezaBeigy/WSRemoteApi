import json
import cbor2 as cbor
from websockets import connect

class CustomDict(dict):
    def __getattr__(self, name):
        if name in self:
            return self[name]
        raise AttributeError(f"object has no attribute '{name}'")

class RemoteAPIClient:
    def __init__(self, host='localhost', port=23050, codec="cbor", **opts):
        self.host = host
        self.port = port
        self.codec = codec
        self.opts = opts
        self.ws = None

        if codec == "cbor":
            self.pack_message = cbor.dumps
            self.unpack_message = cbor.loads
        elif codec == "json":
            self.pack_message = json.dumps
            self.unpack_message = json.loads
        else:
            raise ValueError("Invalid codec")

    async def connect(self):
        self.ws = await connect(f"ws://{self.host}:{self.port}")

    async def close(self):
        if self.ws:
            await self.ws.close()

    async def call(self, func, args):
        message = self.pack_message({"func": func, "args": args})
        await self.ws.send(message)
        response = await self.ws.recv()
        reply = self.unpack_message(response)
        if reply.get("success"):
            return reply.get("ret")
        else:
            raise Exception(reply.get("error"))

    async def getObject(self, name):
        r = await self.call('wsRemoteApi.info', [name])
        return self.get_object_(name, r[0])

    def get_object_(self, name, _info):
        ret = {}
        for k, v in _info.items():
            if len(v) == 1 and 'func' in v:
                async def method(*args, func_name=f"{name}.{k}"):
                    return await self.call(func_name, args)

                ret[k] = method
            elif len(v) == 1 and 'const' in v:
                ret[k] = v['const']
            else:
                async def get_nested_object():
                    return await self.getObject(f"{name}.{k}")

                ret[k] = get_nested_object()
        return CustomDict(ret)

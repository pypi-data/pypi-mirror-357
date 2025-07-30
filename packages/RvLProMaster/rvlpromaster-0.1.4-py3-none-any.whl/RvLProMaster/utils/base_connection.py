import asyncio
import aiohttp

class BaseConnectionError(Exception):
    def __init__(self, message, status=None, response_data=None):
        super().__init__(message)
        self.status = status
        self.response_data = response_data

    def __str__(self):
        base = super().__str__()
        if self.status:
            base += f" (HTTP {self.status})"
        return base


class SyncClientResponse:
    def __init__(self, data, status):
        self._data = data
        self._status = status

    def json(self):
        return self._data

    def status(self):
        return self._status


class SyncRequestContext:
    def __init__(self, method, loop, session, url, **kwargs):
        self.method = method
        self.loop = loop
        self.session = session
        self.url = url
        self.kwargs = kwargs
        self.response = None

    def __enter__(self):
        self.response = self.loop.run_until_complete(self._do_request())
        return self.response

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    async def _do_request(self):
        try:
            async with self.session.request(self.method, self.url, **self.kwargs) as resp:
                try:
                    data = await resp.json()
                except aiohttp.ContentTypeError:
                    data = await resp.text()

                if resp.status >= 400:
                    raise BaseConnectionError(
                        f"HTTP error for {self.method.upper()} {self.url}",
                        status=resp.status,
                        response_data=data
                    )

                return SyncClientResponse(data, resp.status)
        except aiohttp.ClientError as e:
            raise BaseConnectionError(f"Network error: {e}")
        except asyncio.TimeoutError:
            raise BaseConnectionError("Request timeout")
        except Exception as e:
            raise BaseConnectionError(f"Unexpected error: {e}")


class BaseConnection:
    def __enter__(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.session = self.loop.run_until_complete(self._create_session())
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.loop.run_until_complete(self.session.close())
        self.loop.close()

    async def _create_session(self):
        return aiohttp.ClientSession()

    def post(self, url, **kwargs):
        return SyncRequestContext("post", self.loop, self.session, url, **kwargs)

    def get(self, url, **kwargs):
        return SyncRequestContext("get", self.loop, self.session, url, **kwargs)

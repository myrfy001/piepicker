# coding:utf-8
import json
from typing import Optional, Any, List, Dict, Union, Type, Iterable
from types import TracebackType
import asyncio

import warnings


import pyppeteer
from aiohttp.typedefs import StrOrURL, LooseCookies, JSONEncoder
from aiohttp.abc import AbstractCookieJar

from piepicker.client_reqrep import ClientResponse, ClientRequest


class ClientSession:
    def __init__(self, *,
                 browser_ws_endpoint: Optional[str] = None,
                 pyppeteer_options: Optional[Dict] = None,
                 pyppeteer_kwargs: Optional[Dict] = None,
                 incognito: bool = False,
                 loop: Optional[asyncio.AbstractEventLoop] = None,
                 cookies: Optional[LooseCookies] = None,
                 json_serialize: JSONEncoder = json.dumps,
                 request_class: Type[ClientRequest] = ClientRequest,
                 response_class: Type[ClientResponse] = ClientResponse,
                 cookie_jar: Optional[AbstractCookieJar] = None,
                 raise_for_status: bool = False,
                 trust_env: bool = False,
                 **kwargs: Any) -> None:
        if kwargs:
            warnings.warn(f'the kw arguments {",".join(kwargs.keys())} is not'
                          'supported by pyppeteer render',
                          Warning,
                          stacklevel=2)

        self.browser_ws_endpoint = browser_ws_endpoint
        self.pyppeteer_options = (
            pyppeteer_options if pyppeteer_options is not None else {})
        self.pyppeteer_kwargs = (
            pyppeteer_kwargs if pyppeteer_kwargs is not None else {})
        self.incognito = incognito
        self.loop = loop
        self.cookies = cookies
        self.json_serialize = json_serialize
        self.request_class = request_class
        self.response_class = response_class
        self.cookie_jar = cookie_jar
        self.raise_for_status = raise_for_status
        self.trust_env = trust_env
        self.browser = None
        self.browser_context = None

    async def get(self, url: StrOrURL,  **kwargs: Any):
        request = self.request_class(url, self, **kwargs)
        response = await request.request()
        return response

    async def init_session(self):
        if self.browser is not None:
            return
        if self.browser_ws_endpoint is None:
            self.browser = await pyppeteer.launch(
                options=self.pyppeteer_options,
                **self.pyppeteer_kwargs)
        else:
            options = {'browserWSEndpoint': self.browser_ws_endpoint}
            options.update(self.pyppeteer_options)
            self.browser = await pyppeteer.connect(
                options=options,
                **self.pyppeteer_kwargs
            )

        if self.incognito:
            self.browser_context = (
                await self.browser.createIncognitoBrowserContext())
        else:
            self.browser_context = self.browser.browserContexts[0]

    async def close(self):
        if self.browser is None:
            return
        if self.browser_ws_endpoint is None:
            await self.browser.close()
        else:
            await self.browser.disconnect()

    async def __aenter__(self) -> 'ClientSession':
        await self.init_session()
        return self

    async def __aexit__(self,
                        exc_type: Optional[Type[BaseException]],
                        exc_val: Optional[BaseException],
                        exc_tb: Optional[TracebackType]) -> None:
        await self.close()


class PageContextManager:
    pass

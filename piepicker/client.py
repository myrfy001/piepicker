# coding:utf-8

from typing import Optional
from aiohttp import ClientSession as AioClientSession
from piepicker.pyppeteer_session import ClientSession as PyppeClientSession


class ClientSession:
    def __new__(cls, *,
                render: Optional[str] = None,
                **kwargs) -> None:
        if render is None:
            return AioClientSession(**kwargs)
        elif render == 'pyppetter':
            return PyppeClientSession(**kwargs)
        else:
            raise Exception('render not known')

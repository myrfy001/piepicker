import asyncio
import contextlib
import gc
import json
import re
import time
from http.cookies import SimpleCookie
from io import BytesIO
import subprocess
from unittest import mock

import pytest
from multidict import CIMultiDict, MultiDict
from yarl import URL

import aiohttp
from aiohttp import client, hdrs, web
from piepicker.client import ClientSession
from aiohttp.client_reqrep import ClientRequest
from aiohttp.connector import BaseConnector, TCPConnector
from aiohttp.helpers import DEBUG, PY_36


@pytest.fixture
def connector(loop):
    async def make_conn():
        return BaseConnector(loop=loop)
    conn = loop.run_until_complete(make_conn())
    proto = mock.Mock()
    conn._conns['a'] = [(proto, 123)]
    yield conn
    conn.close()


@pytest.fixture
def create_session(loop):
    session = None

    async def maker(*args, **kwargs):
        nonlocal session
        session = ClientSession(*args, loop=loop, render='pyppetter',
                                pyppeteer_options={'headless': False},
                                **kwargs)
        await session.init_session()
        return session
    yield maker
    if session is not None:
        loop.run_until_complete(session.close())


@pytest.fixture
def session(create_session, loop):
    return loop.run_until_complete(create_session())


@pytest.fixture
def params():
    return dict(
        headers={"Authorization": "Basic ..."},
        max_redirects=2,
        encoding="latin1",
        version=aiohttp.HttpVersion10,
        compress="deflate",
        chunked=True,
        expect100=True,
        read_until_eof=False)


@pytest.fixture(scope="session")
def test_http_server():
    child = subprocess.Popen(
        ['python', '-m', 'http.server', '39999'])
    yield child
    child.terminate()
    child.wait()


async def test_http_GET(session, test_http_server) -> None:

    resp = await session.get("http://127.0.0.1:39999/tests/sample_htmls/dynamic_dom.html")
    assert resp.resource_responses[0].url == 'http://127.0.0.1:39999/tests/sample_htmls/dynamic_dom.html'
    context = await resp.resource_responses[0].text()
    assert '<body>' not in context
    assert 'document.write' in context
    assert 'add dom node' in await resp.text()

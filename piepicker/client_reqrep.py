# coding:utf-8
from typing import Any
from pyppeteer.page import Page


class ClientRequest:
    def __init__(self, url, session: 'ClientSession', **kwargs: Any):
        self.url = url
        self.session = session
        self.kwargs = kwargs

    async def request(self):
        page = await self.session.browser_context.newPage()
        response = self.session.response_class(
            page, self.session, self, **self.kwargs)

        page.on(Page.Events.Response, response._add_resource_response)
        await page.goto(self.url)

        return response


class ClientResponse:
    def __init__(self, page, session, request, **kwargs):
        self.page = page
        self.session = session
        self.request = request
        self.kwargs = kwargs

        self.resource_responses = []

    def _add_resource_response(self, response):
        self.resource_responses.append(response)

    async def text(self):
        return await self.page.content()

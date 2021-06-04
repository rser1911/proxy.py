# -*- coding: utf-8 -*-
"""
    proxy.py
    ~~~~~~~~
    ⚡⚡⚡ Fast, Lightweight, Pluggable, TLS interception capable proxy server focused on
    Network monitoring, controls & Application development, testing, debugging.

    :copyright: (c) 2013-present by Abhinav Singh and contributors.
    :license: BSD, see LICENSE for more details.
"""
from typing import Optional, Any

from proxy.common.utils import build_http_response
from proxy.http.parser import HttpParser
from proxy.http.codes import httpStatusCodes
from proxy.http.proxy import HttpProxyBasePlugin

from proxy.http.methods import httpMethods
from proxy.http.exception import HttpRequestRejected

from os import environ

class ThroughtPhpScriptPlugin(HttpProxyBasePlugin):

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.proxy_host = b''
        self.proxy_ip = b''
        self.proxy_pass = b''
        self.proxy_url = b''
        self.proxy_nocheck = False

        if 'PROXY_HOST' in environ:
            self.proxy_host = environ['PROXY_HOST'].encode()
        if 'PROXY_IP' in environ:
            self.proxy_ip = environ['PROXY_IP'].encode()
        if 'PROXY_PASS' in environ:
            self.proxy_pass = environ['PROXY_PASS'].encode()
        if 'PROXY_URL' in environ:
            self.proxy_url = environ['PROXY_URL'].encode()
        if 'PROXY_NOCKECK' in environ:
            self.proxy_nocheck = True

    def before_upstream_connection(
            self, request: HttpParser) -> Optional[HttpParser]:

        request.port = 443
        if self.proxy_ip == b'':
            request.host_upstream = self.proxy_host
        else:
            request.host_upstream = self.proxy_ip
        return request

    def handle_client_request(
            self, request: HttpParser) -> Optional[HttpParser]:

        if request.method != httpMethods.CONNECT:
            host = request.headers[b'host'][1]
            shema = b'https://'

            if request.url.path[0:8] == b'/favicon' or host == b'retracker.local':
                raise HttpRequestRejected(status_code=httpStatusCodes.NOT_FOUND,
                        reason=b'', headers={b'Connection': b'close'})

            if request.host_upstream != None:
                request.add_header(b'X-Test-Sheme', b'1')
                shema = b'http://'

            url = request.url.path
            if request.url.query != b'':
                url = url + b'?' + request.url.query

            request.set_url(b'https://' + self.proxy_host + self.proxy_url)
            request.add_header(b'X-Test-Url', url)
            request.add_header(b'X-Test-Pass', self.proxy_pass)
            request.add_header(b'X-Test-Host', host)
            request.del_header(b'Host')
            request.add_header(b'Host', self.proxy_host)

            print((shema + host + url).decode())
            # print(str(request.headers) + '\n\n')

        request.host_upstream = self.proxy_host
        if self.proxy_nocheck:
            request.host_upstream_nocheck = True
        return request

    def handle_upstream_chunk(self, chunk: memoryview) -> memoryview:
        # print(chunk.tobytes())
        return chunk

    def on_upstream_connection_close(self) -> None:
        pass

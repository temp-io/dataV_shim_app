# -*- coding: utf-8
#  Copyright 2012 Paulo Alem<biggahed@gmail.com>
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from tornado import gen
from tornado.log import gen_log
from tornado.httpclient import HTTPError
from tornado.httpclient import HTTPRequest
from tornado.httpclient import AsyncHTTPClient


try:
    import urllib.parse as urllib
except ImportError:
    import urllib

try:
    import json
except ImportError:
    import simplejson as json


BASE_URL = 'https://api.temp-io.life'


class TempAPI(object):
    def __init__(self, access_token=None):
        self.access_token = access_token

    @gen.coroutine
    def api(self, path, **kwargs):
        try:
            import time
            s_time = time.time()
            data = yield self._make_request(path, **kwargs)
            e_time = time.time()
            gen_log.info("=====Time request wio api, {}".format(float(e_time)-float(s_time)))
        except Exception as e:
            gen_log.error(e)
            raise
        raise gen.Return(data)

    @gen.coroutine
    def _make_request(self, path, query=None, method="GET", body=None, headers=None, **kwargs):
        """
        Makes request on `path` in the graph.

        path -- endpoint to the facebook graph api
        query -- A dictionary that becomes a query string to be appended to the path
        method -- GET, POST, etc
        body -- message body
        headers -- Like "Content-Type"
        """
        if not query:
            query = {}

        if self.access_token:
            query["access_token"] = self.access_token

        query_string = urllib.urlencode(query) if query else ""
        if method == "GET":
            body = None
        else:
            if headers and "json" in headers.get('Content-Type'):
                body = json.dumps(body) if body else ""
            else:
                body = urllib.urlencode(body) if body else ""

        url = BASE_URL + path
        if query_string:
            url += "?" + query_string

        # url = "https://wio.temp-io.life/v1/nodes/create?access_token=123"
        gen_log.info("URL=====> {}".format(url))
        gen_log.info("method=====> {}".format(method))
        gen_log.info("body=====> {}".format(body))

        client = AsyncHTTPClient()
        request = HTTPRequest(url, method=method, body=body, headers=headers, **kwargs)
        try:
            response = yield client.fetch(request)
        except HTTPError as e:
            raise WioAPIError(e)
        except Exception as e:
            gen_log.error(e)
            raise

        content_type = response.headers.get('Content-Type')
        gen_log.info("#### content_type: {}".format(content_type))
        gen_log.info("#### body: {}".format(response.body))
        if 'json' in content_type:
            data = json.loads(response.body.decode())
        else:
            raise WioAPIError('Maintype was not json')

        raise gen.Return(data)


# noinspection PyBroadException
class WioAPIError(Exception):
    def __init__(self, error):
        self.error = error
        try:
            data = json.loads(self.error.response.body)
            try:
                self.message = data["error"]
            except:
                self.message = data
        except:
            self.message = self.error

        Exception.__init__(self, self.message)

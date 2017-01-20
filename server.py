#!/usr/bin/env python
# coding=utf-8
import json
import tornado.ioloop
import tornado.web
from tornado_cors import CorsMixin
from tornado import gen
from tornado.log import gen_log
from tornado.options import define
from tornado.options import options
from tempapi import TempAPI
define("port", type=int, default=8101, help="Run server on a specific port")
define("debug", type=int, default=1, help="0:false, 1:true")


class MainHandler(CorsMixin, tornado.web.RequestHandler):
    CORS_ORIGIN = '*'
    CORS_HEADERS = 'Content-Type, Authorization'

    @gen.coroutine
    def get(self):
        u1 = self.get_argument('u1', None)
        u2 = self.get_argument('u2', None)
        url1 = '/v1/users/{}/temps/{}'.format(u1.split(',')[0], u1.split(',')[1])
        url2 = '/v1/users/{}/temps/{}'.format(u2.split(',')[0], u2.split(',')[1])

        print url1, url2
        t = TempAPI()
        temp1 = yield t.api(url1)
        temp2 = yield t.api(url2)
        data = [
            {
                'x': temp1['name'],
                'y': temp1['temperature'],
                's': '1'
            },
            {
                'x': temp2['name'],
                'y': temp2['temperature'],
                's': '2'
            }
        ]
        self.set_status(200)
        self.set_header('Content-Type', 'application/json; charset=UTF-8')
        self.finish(json.dumps(data, indent=4))


def make_app():
    setting = dict(
        debug=True if options.debug else False,
        login_url='/',
    )
    return tornado.web.Application([
        (r"/dataV_ship/temps", MainHandler)
    ], **setting)


if __name__ == "__main__":
    from tornado.log import enable_pretty_logging

    enable_pretty_logging()
    options.parse_command_line()
    gen_log.info("http://localhost:{}".format(options.port))
    app = make_app()
    app.listen(options.port)
    tornado.ioloop.IOLoop.current().start()

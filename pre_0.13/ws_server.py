
import zmq
from zmq.eventloop import ioloop, zmqstream
ioloop.install()


import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web

import tornado

if tornado.version_info <= (2,1,1):

    def _execute(self, transforms, *args, **kwargs):
        from tornado.websocket import WebSocketProtocol8, WebSocketProtocol76
        
        self.open_args = args
        self.open_kwargs = kwargs

        # The difference between version 8 and 13 is that in 8 the
        # client sends a "Sec-Websocket-Origin" header and in 13 it's
        # simply "Origin".
        if self.request.headers.get("Sec-WebSocket-Version") in ("7", "8", "13"):
            self.ws_connection = WebSocketProtocol8(self)
            self.ws_connection.accept_connection()
            
        elif self.request.headers.get("Sec-WebSocket-Version"):
            self.stream.write(tornado.escape.utf8(
                "HTTP/1.1 426 Upgrade Required\r\n"
                "Sec-WebSocket-Version: 8\r\n\r\n"))
            self.stream.close()
            
        else:
            self.ws_connection = WebSocketProtocol76(self)
            self.ws_connection.accept_connection()

    tornado.websocket.WebSocketHandler._execute = _execute
    del _execute

ctx = zmq.Context()
s = ctx.socket(zmq.REP)
s.bind('tcp://127.0.0.1:55550')
stream = zmqstream.ZMQStream(s)

class WSHandler(tornado.websocket.WebSocketHandler):

    def open(self):
    	print 'new connection'
        stream.on_recv(self.send_ZMQ_message)
    	#self.write_message("Hello World")
      
    def on_message(self, message):
    	print 'message received %s' % message

    def on_close(self):
      print 'connection closed'

    def send_ZMQ_message(self, msg):
        #print "get msg: %s" % msg
        self.write_message(msg[0]) # send the messdage recevied from ZMW to browser through websocket
        s.send("msg sent")


application = tornado.web.Application([
    (r'/ws', WSHandler),
])


if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(55551)
    tornado.ioloop.IOLoop.instance().start()

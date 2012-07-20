IPython Notebook and d3.js Mashup
=================================

This note demostrate on the possibility to use the ipython notebook web interface to make some potential useful visulization with d3.js (or other javascript library.)  


Bridging ZMQ and Websocket 
---------------------------------
The basic idea is to see if we can send javascript code directly from the notebook to an IFRAME or sperated window to make the browser excuting the javascript code accordingly. To make it happen, the setup is pretty similar to the ipython notebook itself. We need a backend server that receive message throgh zmq, and the server needs to pass the message (javascript code) to the frontend web page. If you are already running ipython notebook, the pyzmq and tornado are already installed, you can run the code below as the server bridging zmq and websocket.  Here is the `ws_server.py` looks like, 


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


Client Side HTML
--------------------------

The code above will listen to port 55550 on a zmq REQ/REP pair connect and send what it recived to a websocket connection. On the browser side, we need to have a simple html page that connect to the web-socket.  Here is the simple `client.html` code.

    
    <html>
    <head>
        <script>
            if (typeof(WebSocket) !== 'undefined') {
                theWebSocket = WebSocket;
            } else if (typeof(MozWebSocket) !== 'undefined') {
                theWebSocket = MozWebSocket;
            } else {
                alert('Your browser does not have WebSocket support, please try Chrome, Safari or Firefox ≥ 6. Firefox 4 and 5 are also supported by you have to enable WebSockets in about:config.');
            };
            var ws = new theWebSocket("ws://localhost:55551/ws");
            ws.onopen = function() {
                    ws.send("connected");
            };
            ws.onmessage = function(event) {
                    //alert("The server sent a message: " + event.data);
                    eval(event.data)
            };
        </script>
    </head>
    <body>
    </body>
    </html>

The brower will excute any javascript that it has recieved with this html page. (Beware, it is not secure. Play it with caution.) 

Help Classes Within IPython
------------------------------
To make ipython notebook display a html page, it might be convient to add some of the classes in the `IPython.core.display` module. This two classes can load an HTML page to a IFRAME or a new brower window which can show some of the javascript tricks that we want the browser to play.  You will need to edit your IPython/core/display.py to add these two classes.  

    class IFRAME(DisplayObject):
    
        def _repr_html_(self):
            if self.url:
                return '<iframe src="{0}" width=1000px height=600px></iframe>'.format(self.url)
            else:
                iframeStem = '<iframe src="data:text/html;base64,{0}" width=1000px height=600px></iframe>'
                data_uri = iframeStem.format(self.data.encode("base64").replace("\n", ""))
                return data_uri
    
    class NEWWINDOW(DisplayObject):
    
        def _repr_html_(self):
            if self.url:
                return '<script>window.open("{0}","ipython_display")</script>'.format(self.url)
            else:
                iframeStem = '<script>window.open("data:text/html;base64,{0}","ipython_display")</script>'
                data_uri = iframeStem.format(self.data.encode("base64").replace("\n", ""))
                return data_uri


Start the Servers
---------------------------
Before we run this example, we need to start the ipython notebook and the `ws_server.py`.

    $ ipython notebook &
    $ python ws_server.py &

Here is the content I have in the current working directory where I start the ipython notebook and the `ws_server.py`.

    $ ls
    client.html     
    colorbrewer.css 
    colorbrewer.js  
    d3.js           
    example.ipynb   
    ws_server.py
    images/


Now, you can load the `example.ipynb` from the ipython notebook web interface. You can run the notebook cell by cell to see how to create some d3.js visulization step by step with ipython.  There are a lot of possible ways to make such thing working better.  

# MTSL

MTSL is an easy-to-use, relatively simple, low blast radius security layer.

It works similar to the TLS socket wrapper from `ssl`.

Example:

```python
from mtsl import MTSLContext
import socket

ctx = MTSLContext()
ctx.authority_file("authority.pub.elle")
ctx.subject_files('subject.pub.elle', 'subject.sec.elle')

sock = socket.socket()

sock.connect('12.34.56.78')

secure_sock = ctx.wrap_socket(sock)

# send/recv works from here
# conn from `socket.accept()` works this way as well

sock.listen()
while 1:
    c, addr = sock.accept()
    with ctx.wrap_socket(c) as secure_conn:
        pass  # send/recv works from here
```

Read source code for full technical details if you're a nerd like me.  
Or just float off into the ether and accept that I had to know what I was doing so you don't.

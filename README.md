# pyrpc

Easy-to-use python RPC.

## Server example

```python
from pyrpc import Server

def func_a():
    pass

def func_b():
    pass

def func_c():
    pass

s = Server()
functions = [func_a, func_b, func_c]

for f in functions:
    s.add_function(f)

s.start()
```

## Client example

```python
from pyrpc import Client

c = Client()
c.connect()

c.func_a()
c.func_b()
c.func_c()

c.close()
```

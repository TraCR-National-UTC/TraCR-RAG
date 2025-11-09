import time

def example_function():
    yield "Message 1"
    time.sleep(1)
    yield "Message 2"
    time.sleep(1)   
    yield "Message 3"
    time.sleep(1)
    yield "Message 4"
    time.sleep(1)
    yield "Message 5"

    return


for msg in example_function():
    print(msg)
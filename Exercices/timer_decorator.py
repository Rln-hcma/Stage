import time

def timer(func):
    def wrapper(*args, **kargs):
        t1 = time.perf_counter() #start
        func(*args, **kargs)
        
        for i in range(10):
            time.sleep(0.5)
            
        func(*args, **kargs)
        t2 = time.perf_counter() #stop
        print(f"Time elapsed = {(t2-t1)/10**9:.9f} nsec.")
    return wrapper
        
@timer
def filter_positive():
    for i in [7,-8,5,-3]:
        if i >0:
            print(i)
    


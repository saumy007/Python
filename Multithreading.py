import threading 
import time

def func(seconds):
    print(f"sleeping for {seconds} ")
    time.sleep(seconds)
    print("saumy")

#Normal Code
#func(5)
#func(2)
#func(3)

#code Using threads
t1 = threading.Thread(target=func, args=[5])
t2 = threading.Thread(target=func, args=[2])
t3 = threading.Thread(target=func, args=[3])
t1.start()
t2.start()
t3.start()
t1.join()
t2.join()
t3.join()
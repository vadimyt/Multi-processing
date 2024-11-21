import multiprocessing
import numpy as np
from contextlib import closing
import os

def __init(shared_arr_):
    global shared_arr
    shared_arr = shared_arr_

def __shared_to_numpy(shared_arr, dtype, shape):
    return np.frombuffer(shared_arr, dtype=dtype).reshape(shape)

def __create_shared_array(dtype, shape):
    dtype = np.dtype(dtype)
    cdtype = np.ctypeslib.as_ctypes_type(dtype)
    shared_arr = multiprocessing.RawArray(cdtype, sum(shape))
    arr = __shared_to_numpy(shared_arr, dtype, shape)
    return shared_arr, arr

def __create_shared_array_from_array(array:np.ndarray):
    shared_arr, arr = __create_shared_array(array.dtype, array.shape)
    for i,val in enumerate(array):
        shared_arr[i]=val
    return shared_arr, arr

def __shared_sum(tuple):
    x, y = tuple
    arr = __shared_to_numpy(*shared_arr)
    arr[x]=arr[x]+arr[y]

def __generate_layer_pairs(j):
    layer = []
    i = 0
    while i<j:
        layer.append((i,j))
        i+=1
        j-=1
    return layer

def sum_array(arr:np.ndarray):
    sum:int = 0
    for val in arr:
        sum += val
    return sum

def parallel_sum_array_piramid(arr:np.ndarray, workers = os.cpu_count()):
    shared_arr, local_arr = __create_shared_array_from_array(arr)
    n = local_arr.size
    while(n!=1):
        j=n-1
        with closing(multiprocessing.Pool(
            workers, initializer=__init, initargs=((shared_arr, local_arr.dtype, local_arr.shape),))) as p:
            p.map(__shared_sum, __generate_layer_pairs(j))
        p.join()
        n = int((n+1)/2)
    return local_arr[0]


def parallel_sum_array_batch(arr:np.ndarray, workers = os.cpu_count()):
    shape = arr.shape[0]
    if shape == 1:
        return arr[0]
    if shape <= workers:
        return sum_array(arr)
    batch_len=int(shape/workers)
    batch = [arr[0:(1)*batch_len]]
    for i in range(0,workers):
        if i+1 == workers:
            if shape%workers!=0:
                batch.append(arr[(i+1)*batch_len:])
        else:
            batch.append(arr[(i+1)*batch_len:(i+2)*batch_len])
    with closing(multiprocessing.Pool(
            len(batch))) as p:
            sums = p.map(sum_array, batch)
    p.join()
    sum = sum_array(np.array(sums, arr.dtype))
    return(sum)

def task(array_size = 10, workers = os.cpu_count(), repeat = 1):
    import time
    multiprocessing.freeze_support()
    timeA = 0
    timeB = 0
    timeC = 0
    repeat = repeat

    start_time = time.time()
    arr = np.random.randint(100,size=array_size, dtype=np.int64)
    end_time = time.time()
    print("Time took to generate array of size %i:" % (array_size))
    print("--- %s seconds ---" % (end_time - start_time))

    print("Initial array: ")
    print(arr)

    print('\n')

    for i in range(repeat):
        start_time = time.time()
        print(sum_array(arr))
        end_time = time.time()
        print("Simple sum: " + str(i+1) +"/"+str(repeat))
        timeA += end_time - start_time

    # for i in range(repeat):
    #     start_time = time.time()
    #     print(parallel_sum_array_piramid(arr, workers))        
    #     end_time = time.time()
    #     print("Piramidal sum: " + str(i+1) +"/"+str(repeat))
    #     timeB += end_time - start_time

    for i in range(repeat):
        start_time = time.time()
        print(parallel_sum_array_batch(arr, workers))
        end_time = time.time()
        print("Batch sum: " + str(i+1) +"/"+str(repeat))
        timeC += end_time - start_time

    print("Simple sum:")
    print("--- %s seconds ---" % (timeA/repeat))
    # print("Piramidal sum:")
    # print("--- %s seconds ---" % (timeB/repeat))
    print("Batch sum:")
    print("--- %s seconds ---" % (timeC/repeat))

    return (timeA/repeat)*1000, (timeB/repeat)*1000, (timeC/repeat)*1000

def create_test_args(start_array_size = 100000, stop_array_size = 4000000, step = None, max_workers = os.cpu_count()):
    args = []
    if (step == None):
        step = start_array_size
    for array_size in range(start_array_size,stop_array_size+step,step):
        args.append([])
        for workers in range(1,max_workers+1):
            args[len(args)-1].append((array_size, workers))
    return args

def graph(start, stop, max_workers = os.cpu_count()):
    import math
    from matplotlib import pyplot as plt
    from matplotlib.ticker import MaxNLocator
    args = create_test_args(start, stop, max_workers=max_workers)
    x = []
    y1 = []
    y2 = []
    y3 = []
    for val in args:
        for array_size,workers in val:
            x.append(workers)
            c_time, p_time, b_time = task(array_size,workers, 10)
            y1.append(c_time)    
            #y2.append(p_time) 
            y3.append(b_time) 
        fig, ax = plt.subplots()
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        if (len(y1)>1):
            ax.plot(x, y1, linewidth=2.0, color="red", label="consistent")
        if (len(y2)>1):
            ax.plot(x, y2, linewidth=2.0, color="green", label="piramidal")
        if (len(y3)>1):
            ax.plot(x, y3, linewidth=2.0, color="blue", label="batch")
        ax.set_title("Array size: " + str(val[0][0]))
        ax.set_xlabel("Workers")
        ax.set_ylabel("Time (ms)")
        fig.legend()
        fig.show()
        x.clear()
        y1.clear()
        y2.clear()
        y3.clear()
    input()

if __name__ == "__main__":
    graph(10000000,10000000)
    graph(1000000,1000000)
    graph(100000,100000)
    graph(10000,10000)
    #task(100000000)
    #print(np.array([1,2,1,2,1,2,1,2,1,2,1,2,1,21,1,21,2]).sum())
    #print(parallel_sum_array_batch(np.random.randint(100,size=100000000, dtype=np.int64),16))
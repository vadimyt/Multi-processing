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

def task(array_size = 10, workers = os.cpu_count()):
    import time
    multiprocessing.freeze_support()

    start_time = time.time()
    arr = np.random.randint(100,size=array_size)
    arr.astype(np.int64)
    end_time = time.time()
    print("Time took to generate array of size %i:" % (array_size))
    print("--- %s seconds ---" % (end_time - start_time))

    print("Initial array: ")
    print(arr)

    print('\n')

    start_time = time.time()
    print(arr.sum())
    end_time = time.time()
    print("Numpy built-in sum:")
    print("--- %s seconds ---" % (end_time - start_time))

    start_time = time.time()
    print(sum_array(arr))
    end_time = time.time()
    print("Simple sum:")
    print("--- %s seconds ---" % (end_time - start_time))

    start_time = time.time()
    print(parallel_sum_array_piramid(arr, workers))
    end_time = time.time()
    timeA = end_time - start_time
    print("Parallel sum:")
    print("--- %s seconds ---" % (end_time - start_time))

    print('\n')

    return timeA

def create_test_args(start_array_size = 100000, stop_array_size = 1000000, step = None, max_workers = os.cpu_count()):
    args = []
    if (step == None):
        step = start_array_size
    for array_size in range(start_array_size,stop_array_size+step,step):
        for workers in range(1,max_workers+1):
            args.append((array_size, workers))
    return args

def graph():
    import math
    from matplotlib import pyplot as plt
    args = create_test_args(100, 300, max_workers=2)
    x = []
    y = []
    z = {}
    for array_size,workers in args:
        x.append(array_size)
        y.append(workers)
        z[(array_size,workers)]=task(array_size,workers)*100
    
    xgrid, ygrid = np.meshgrid(x, y)
    zgrid = []
    for j in range(len(xgrid)):
            zgrid.append([])
    for k in range(len(zgrid)):
        for l in range(len(xgrid[k])):
            try:
                zgrid[k].append(z[(xgrid[k][l],ygrid[k][l])])
            except:
                zgrid[k].append(np.NaN)

    fig, ax = plt.subplots()
    vmin = math.floor(z[min(z)])
    vmax = math.ceil(z[max(z)])
    num = 100
    contourf_ = ax.contourf(xgrid, ygrid, zgrid, levels=np.linspace(vmin,vmax,num),extend='max')
    cbar = fig.colorbar(contourf_,ticks=range(vmin, vmax+1, 10))
    t = fig.get_axes()[0].axes
    t.set_xlabel("Array size")
    t.set_ylabel("Workers")
    fig.show()
    input()

if __name__ == "__main__":
    task()
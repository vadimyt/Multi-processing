import multiprocessing


def sum(arr:list):
    copy = arr.copy()
    sum = copy.pop()
    for val in copy:
        sum+=val
    return sum

def threaded_sum(arr:list, workers = 2):
    copy = arr.copy()
    while(len(copy) != 1):
        localArr = []
        if len(copy)%2!=0:
            localArr.append([0,copy.pop()])
        for i in range(0,len(copy),2):
            localArr.append([copy[i],copy[i+1]])
        pool_obj = multiprocessing.Pool(workers) 
        results = pool_obj.map(sum, localArr)
        pool_obj.close()
        pool_obj.join()
        copy = results
    return(copy.pop())

def generate_list(n:int, a=-100, b=100):
    import random
    list = []
    for i in range(n):
        list.append(random.randint(a,b))
    return list

if __name__ == "__main__":
    import time
    array = generate_list(1000)

    start_time = time.time()
    print(sum(array))
    end_time = time.time()
    print("--- %s seconds ---" % (end_time - start_time))

    # start_time = time.time()
    # print(threaded_sum(array))
    # end_time = time.time()
    # print("--- %s seconds ---" % (end_time - start_time))

    # start_time = time.time()
    # print(threaded_sum(array, 4))
    # end_time = time.time()
    # print("--- %s seconds ---" % (end_time - start_time))

    # start_time = time.time()
    # print(threaded_sum(array, 8))
    # end_time = time.time()
    # print("--- %s seconds ---" % (end_time - start_time))

    start_time = time.time()
    print(threaded_sum(array, 16))
    end_time = time.time()
    print("--- %s seconds ---" % (end_time - start_time))
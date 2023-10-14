import threading
import time

def quicksort(array):
    if len(list(array)) <= 1:
        return array
    pivot = array[len(array) // 2]
    left = [x for x in array if x < pivot]
    middle = [x for x in array if x == pivot]
    right = [x for x in array if x > pivot]
    return quicksort(left) + middle + quicksort(right)

def quicksort_multi_threading(array):
    if len(list(array)) <= 1:
        return array
    pivot = array[len(array) // 2]
    left = [x for x in array if x < pivot]
    middle = [x for x in array if x == pivot]
    right = [x for x in array if x > pivot]
    left_thread = threading.Thread(target=quicksort_multi_threading,args=(left,))
    right_thread = threading.Thread(target=quicksort_multi_threading,args=(right,))
    left_thread.start()
    right_thread.start()
    left_thread.join()
    right_thread.join()
    return quicksort_multi_threading(left) + middle + quicksort_multi_threading(right)

array = [323,543434,32,4,56,7,76,90]

start_time1 = time.time()
result = quicksort_multi_threading(array)
print(result)
end_time1 = time.time()
print('The Regular quick sort time is: ', end_time1-start_time1, 'Seconds')

start_time2 = time.time()
result2 = quicksort(array)
print(result2)
end_time2 = time.time()
print('The multi Threaded quick sort time is: ',end_time2-start_time2, 'Seconds')
import numpy as np
# find the largest 2 numbers, where their sum closest to 0
#arr_sort = sorted(arr)
#arr=np.array(arr_sort)
arr = [-45, 69, 32, -12, 34, 4]

# # Nastya's answer
# from itertools import combinations
# combin = list(combinations(arr,2)) n * n-1 /2 O(n^2)
# sums = [abs(sum(i)) for i in combin] O(n)
# idx = np.argmin(sums) (O(n)
# print(combin[idx])


# Kit's 
arr_sorted = sorted(arr)
print(arr_sorted)
ans1 = 0 # index of answers
ans2 = len(arr) -1 # index of answers
idxl = 0
idxr = len(arr) -1
sum = arr_sorted[idxl] + arr_sorted[idxr]
while idxr > idxl:
    new_sum = arr_sorted[idxl] + arr_sorted[idxr]
    if abs(sum) > abs(new_sum):
        sum = new_sum
        ans1 = idxl
        ans2 = idxr

    if abs(arr_sorted[idxl]) > abs(arr_sorted[idxr]):
        idxl+=1
    else:
        idxr-=1    

print(ans1)
print(ans2)
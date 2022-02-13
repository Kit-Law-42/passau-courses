class Solution:
    def validMountainArray(self, arr: List[int]) -> bool:
        mx=0
        idx =0
        for i in range(len(arr)):
            if arr[i] > mx:
                mx = arr[i]
                idx =i
        if (mx==arr[0]) or (mx==arr[-1]) :
            return False
        
        for i in range(1, idx+1):
            if arr[i-1] < arr[i]:
                continue
            else:
                return False
        
        for i in range(idx+1, len(arr)):
             if arr[i-1] > arr[i]:
                continue
             else:
                return False
        
        return True
        
        # More beautiful solution
        
        class Solution:
    def validMountainArray(self, arr: List[int]) -> bool:
        #Time: O(n)
        #Space: O(1)
        
        #Have two pointers climb based on these conditions:
        #Move up left ptr if it's on ascending slope
        #Move up right ptr if it's on descending slope
        #If there's only one peak - they'll meet in the middle
        
        left, right = 0, len(arr) - 1
        while left < right:
            #Left ptr climb up
            if arr[left] < arr[left + 1]:
                left += 1
            
            #Right ptr climb up
            elif arr[right - 1] > arr[right]:
                right -= 1
            
            #On a flat surface / Neither ascending nor descending
            else:
                break
            
        return ((left == right) and #See if they meet at the same peak
                (left > 0 and right < len(arr) - 1)) #Handle edge cases it's a straight up/downhill

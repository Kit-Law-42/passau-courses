from typing import List

class Solution:
    def findPoisonedDuration(self, timeSeries: List[int], duration: int) -> int:
        t = 0
        end_sec = 0
        for i in range(len(timeSeries) -1):
            end_sec = timeSeries[i]+duration
            if end_sec > timeSeries[i+1]:
                t -= (end_sec-timeSeries[i+1])
            t += duration
            
        return t+duration
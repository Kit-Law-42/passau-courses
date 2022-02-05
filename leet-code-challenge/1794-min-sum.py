class Solution:
    def countQuadruples(firstString: str, secondString: str):
        map1 = {}
        map2 = {}

        for idx, ch in enumerate(firstString):
            if ch not in map1:
                map1[ch] = idx

        for idx, ch in enumerate(secondString):
                map2[ch] = idx

        min_dist = float('inf')
        cnt =0

        for k in map1.keys():
            if k in map2.keys():
                if min_dist > (map1[k] - map2[k]):
                    min_dist = map1[k] - map2[k]
                    cnt =1
                elif min_dist == (map1[k] - map2[k]):
                    cnt +=1
        
        return cnt
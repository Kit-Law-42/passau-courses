        #Solution 1
        #digits_str=str(digits)[1:-1]
        # digits_str = ''.join([str(i) for i in digits])
        # res = int(digits_str)+1
        # res = list(map(int, str(res)))
        # return res
    
        # Solution 2,
        # total = 0
        # for i in range(len(digits)):
        #     #print(i)
        #     pov = len(digits)-1 -i 
        #     total += digits[i] * 10** pov
        #     # print(total)
        # total+=1
        # return ([int(i) for i in str(total)])
        
#         if digits[-1]!=9:
#             digits[-1] = digits[-1]+1
#             return digits
#         else:
            
#             for i in digits[::-1]:

        # Solution 3, fastest
        for i in range(len(digits)-1 ,-1, -1):
            if digits[i] !=9:
                digits[i] +=1
                return digits
            else:
                digits[i] =0
                if i==0:
                    return [1] + digits
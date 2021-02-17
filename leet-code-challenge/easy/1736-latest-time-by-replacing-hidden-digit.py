# You are given a string time in the form of hh:mm, where some of the digits in the string are hidden (represented by ?).

# The valid times are those inclusively between 00:00 and 23:59.

# Return the latest valid time you can get from time by replacing the hidden digits.

 

# Example 1:

# Input: time = "2?:?0"
# Output: "23:50"
# Explanation: The latest hour beginning with the digit '2' is 23 and the latest minute ending with the digit '0' is 50.
# Example 2:

# Input: time = "0?:3?"
# Output: "09:39"
# Example 3:

# Input: time = "1?:22"
# Output: "19:22"
# class Solution:
#     def maximumTime(self, time: str) -> str:
#         # better to use list(time) to make string mutable.
#         r = []
#         for idx,x in enumerate(time):
#             if x == "?":
#                 if idx==0:
#                     if time[1] >='4' and time[1]!="?":
#                         r.append("1")
#                     else:
#                         r.append("2")
#                 elif idx==1:
#                     if (time[0] =='2' or time[0] =='?'):
#                         r.append("3")
#                     else:
#                         r.append("9")
#                 elif idx==3:
#                     r.append("5")
#                 elif idx==4:
#                     r.append("9")
#             else:
#                 r.append(x)
#         return "".join(r)

class Solution:
    def maximumTime(self, time: str) -> str:
        time = list(time)
        for i in range(len(time)): 
            if time[i] == "?": 
                if i == 0: time[i] = "2" if time[i+1] in "?0123" else "1"
                elif i == 1: time[i] = "3" if time[0] == "2" else "9"
                elif i == 3: time[i] = "5"
                else: time[i] = "9"
        return "".join(time)

a = Solution()
print(a.maximumTime("2?:?0"))
print(a.maximumTime("?0:15"))
print(a.maximumTime("??:3?"))
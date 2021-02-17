# A company is planning to interview 2n people. Given the array costs where costs[i] = [aCosti, bCosti], the cost of flying the ith person to city a is aCosti, and the cost of flying the ith person to city b is bCosti.

# Return the minimum cost to fly every person to a city such that exactly n people arrive in each city.

 

# Example 1:

# Input: costs = [[10,20],[30,200],[400,50],[30,20]]
# Output: 110
# Explanation: 
# The first person goes to city A for a cost of 10.
# The second person goes to city A for a cost of 30.
# The third person goes to city B for a cost of 50.
# The fourth person goes to city B for a cost of 20.

# The total minimum cost is 10 + 30 + 50 + 20 = 110 to have half the people interviewing in each city.
# Example 2:

# Input: costs = [[259,770],[448,54],[926,667],[184,139],[840,118],[577,469]]
# Output: 1859
# Example 3:

# Input: costs = [[515,563],[451,713],[537,709],[343,819],[855,779],[457,60],[650,359],[631,42]]
# Output: 3086

from typing import List


class Solution:
    # def twoCitySchedCost(self, costs: List[List[int]]) -> int:
    #     diffCost  ={}
    #     r =0
    #     for idx, cost in enumerate(costs):
    #         diffCost[idx] = cost[0]- cost[1]
    #     sorted_diffCost = sorted(diffCost.items(), key=lambda item: item[1])
    #     n = len(costs)/2
    #     i=0
    #     for key, values in sorted_diffCost:
    #         if (i <n):
    #             r += costs[key][0]
    #         else:
    #             r +=costs[key][1]
    #         i+=1

    #     return r
    def twoCitySchedCost(self, costs: List[List[int]]) -> int:
        diff =  [costx-costy for costx, costy in costs]
        return sum([costx for costx, _ in costs]) - sum(sorted(diff)[len(costs)//2:])
a = Solution()
print(a.twoCitySchedCost([[10,20],[30,200],[400,50],[30,20]]))
print(a.twoCitySchedCost([[259,770],[448,54],[926,667],[184,139],[840,118],[577,469]]))
print(a.twoCitySchedCost([[515,563],[451,713],[537,709],[343,819],[855,779],[457,60],[650,359],[631,42]]))
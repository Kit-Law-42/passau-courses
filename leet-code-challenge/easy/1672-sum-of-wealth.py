class Solution:
    def maximumWealth(self, accounts: List[List[int]]) -> int:
        sum_of_ac = [sum(ac)for ac in accounts]
        return (max(sum_of_ac))
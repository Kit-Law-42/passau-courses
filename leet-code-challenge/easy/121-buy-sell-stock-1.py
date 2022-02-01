class Solution:
    def maxProfit(self, prices: List[int]) -> int:
        current_min, max_profit_so_far = float('inf'), 0
        for price in prices:
            current_min = min(current_min,  price)
            print(current_min)
            # find the possible max profit by comparing
            # current max and price-current min
            max_profit_so_far = max(max_profit_so_far, price-current_min)
            print(max_profit_so_far)
        return max_profit_so_far

a = Solution()
print(a.maxProfit([7,5,4,3,2]))
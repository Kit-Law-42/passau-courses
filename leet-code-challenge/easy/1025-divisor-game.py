# To prove: if number is even then Alice wins
# Argument 1: If n is 1, alice looses, if n is 2 alice wins
# Argument 2: If n is even, alice can always choose an even divisor and then n-even will also be even which will eventually lead to 2
# # Argument 3: If n is odd, there can only be odd divisor, so whatever Alice chooses, Bob will get chance to play with even 'n' and he will win.

class Solution:
    def divisorGame(self, n: int) -> bool:
        return n%2 ==0
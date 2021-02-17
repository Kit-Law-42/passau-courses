# A robot on an infinite XY-plane starts at point (0, 0) and faces north. The robot can receive one of three possible types of commands:

# -2: turn left 90 degrees,
# -1: turn right 90 degrees, or
# 1 <= k <= 9: move forward k units.
# Some of the grid squares are obstacles. The ith obstacle is at grid point obstacles[i] = (xi, yi).

# If the robot would try to move onto them, the robot stays on the previous grid square instead (but still continues following the rest of the route.)

# Return the maximum Euclidean distance that the robot will be from the origin squared (i.e. if the distance is 5, return 25).

# Note:

# North means +Y direction.
# East means +X direction.
# South means -Y direction.
# West means -X direction.
 

# Example 1:

# Input: commands = [4,-1,3], obstacles = []
# Output: 25
# Explanation: The robot starts at (0, 0):
# 1. Move north 4 units to (0, 4).
# 2. Turn right.
# 3. Move east 3 units to (3, 4).
# The furthest point away from the origin is (3, 4), which is 32 + 42 = 25 units away.

from typing import List


class Solution:
    def robotSim(self, commands: List[int], obstacles: List[List[int]]) -> int:
        obs = set(map(tuple, obstacles))
        # obs = {(x, y) for x, y in obstacles}
        r = 0
        dx, dy = 0, 1
        posx = posy = 0
        for c in commands:
            if c == -1:
                dx, dy = dy, -dx
            elif c == -2:
                dx, dy = -dy, dx
            elif c > 0:
                for _ in range(c):
                    if (posx + dx, posy + dy) in obs:
                        break
                    posx, posy = posx + dx, posy + dy
                r = max(r, posx * posx + posy * posy)
        return r
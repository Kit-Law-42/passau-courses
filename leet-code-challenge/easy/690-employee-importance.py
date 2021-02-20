

# Definition for Employee.
class Employee:
    def __init__(self, id: int, importance: int, subordinates: List[int]):
        self.id = id
        self.importance = importance
        self.subordinates = subordinates


from typing import List


class Solution:
    def getImportance(self, employees: List['Employee'], id: int) -> int:
#         r = 0
#         em = [e for e in employees if e.id == id][0]
#         for sub in em.subordinates:
#             r += self.getImportance(employees, sub)
#         r+= em.importance
        
#         return r
        # use dictionary instead of list to save O(n) to O(1)
        dt = {e.id: e for e in employees}  
        def dfs(id):
            subordinates_importance = sum([dfs(sub_id) for sub_id in dt[id].subordinates])
            return subordinates_importance + dt[id].importance
        return dfs(id)
# Author: Law, Kakit

# My approach:

I implement 2 optimization approach.

1. Chain folding, which fold "Project-Select Task" and "Project-Select-Rename" Task together.
   Select and rename task contains mapper only so we can join them in a single mapper and then add reducer later.
   "JoinBothSelectTask", "JoinRightSelectTask" and "JoinLeftSelectTask" are also basic form of folding.

2. Projection pushdown
   pushdown all projection as far as possible, while maintaining the join key needed.

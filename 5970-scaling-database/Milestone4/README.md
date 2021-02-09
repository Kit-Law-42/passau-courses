# Author: Law, Kakit

# My approach:

I implement 2 optimization approach.

1. Chain folding, which fold "Project-Select Task" and "Project-Select-Rename" Task together.
   Select and rename task contains mapper only so we can join them in a single mapper and then add reducer later.

   "JoinBothSelectTask", "JoinRightSelectTask" and "JoinLeftSelectTask" are also basic form of folding which I implement.
   select task only contain mapper so we merge them together.

2. Projection pushdown
   pushdown all projection as far as possible until they meet select statement, during pushdown maintaining the join key needed.
   as to reduce the data stored in each row.

3. sort table order
   in sql2ra.py, optimize sort the order of table based on the size of the table.
   so after that when hey join together less tuple are generated.

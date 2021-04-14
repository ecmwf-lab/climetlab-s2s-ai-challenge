#!/usr/bin/env python3

from climetlab.utils.availability import Availability

a = Availability("availability.json")

for p in a.iterate():
    print(p)


print()
print(a.tree())

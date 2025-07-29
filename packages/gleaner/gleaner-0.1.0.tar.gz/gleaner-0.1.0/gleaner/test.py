from collections import deque

x = deque("A")
transitions = {
    "A": ["B", "C"],
    "B": ["D"],
    "D": ["H"],
    "C": ["E", "F"],
    "H": [],
    "E": [],
    "F": [],
}

while len(x) > 0:
    a = x.pop()
    t = transitions[a]
    x.extendleft(t)
    print(a)

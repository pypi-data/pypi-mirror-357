# RBTree-Py

A minimal, self-contained **Red-Black Tree** implementation in pure Python.

* **Fast ordered inserts** – `O(log n)` balancing via rotations  
* **Pretty printing** – human-readable ASCII layout  
* **Pluggable keys** – override two small methods to store any comparable object  
* **Property checker** – verifies all five RB-tree invariants  
* **Stress test** – inserts 5 000 random nodes on every run

---

## Installation

1. Open the repository page in your browser.  
2. Download **`rbtree.py`** (look for the **Raw** button or the *Download file* link).  
3. Place `rbtree.py` alongside your own code and import it:

```python
from rbtree import Node, RBTree
```

> No build steps, compilers, or package managers required—just a single file.  
> Works on **Python 3.9 +** with no third‑party dependencies.

---

## Quick start

```python
from rbtree import Node, RBTree

tree = RBTree()
tree.insert(Node(42))
tree.insert(Node(8))
tree.insert(Node(1337))

print(tree)
```

```
========= RBTree
[42 BLACK None]
l:    [8 RED LEFT]
r:    [1337 RED RIGHT]
```

### Run the built‑in stress test

```bash
python -m rbtree          # inserts 5 000 random values and verifies the tree
```

---

## Public API

| Object | Description |
|--------|-------------|
| `class RBTree` | Container with `insert(node)` and `__str__()` |
| `class Node(value)` | Default integer key node |
| `verify_rb_tree(tree)` | Raises `AssertionError` if any RB property fails |
| `test()` | Stress test: populates random nodes & verifies |

---

## Custom keys

Override **two** hooks:

```python
class PersonNode(Node):
    def __init__(self, name: str, age: int):
        super().__init__((name, age))
        self.name, self.age = name, age

    def compare_for_right(self, other: "PersonNode") -> bool:
        return self.age > other.age          # order by age

    def _label(self) -> str:
        return f"{self.name}:{self.age} {self.color}"
```

Everything else—rotations, recolouring, verification—stays the same.

---

## Implementation notes

* Satisfies the five textbook RB-tree rules (enumerated inside the code).  
* Each `Node` tracks `side` (`"LEFT"`, `"RIGHT"`, or `None`) for easy debugging.  
* `verify_rb_tree` depth‑first walks the tree, checking:  
  1. root is black, `parent`/`side` are `None`  
  2. every node is red or black  
  3. red nodes have black children  
  4. equal black‑height on all paths to leaves  
  5. `side` matches actual position  
* Rotations update all pointers and `side` fields so invariants remain intact.

---

## Contributing

1. Fork → feature branch → pull request.  
2. Run `python -m rbtree` before committing (CI rejects failures).  
3. Open issues for ideas or improvements.

---

## License

MIT © 2025 Theo Lincke

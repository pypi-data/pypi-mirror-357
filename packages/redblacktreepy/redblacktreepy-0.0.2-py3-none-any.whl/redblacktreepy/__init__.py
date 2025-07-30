import random

class Node:
    def __init__(self, value):
        self.color = None
        self.parent = None
        self.left = None
        self.right = None
        self.side = None
        self.value = value

    # You can override this
    def compare_for_right(self, node):
        return self.value > node.value

    # You can override this
    def equals(self, node):
        return self.value == node.value

    # You can override this
    def _label(self):
        return f"[{self.value} {self.color} {self.side}]"

    def _pretty(self, level: int = 0) -> str:
        indent = "   " * level
        lines  = [f"{indent}{self._label()}"]

        if level >= 10:
            if self.left or self.right:   
                lines.append(f"{indent}   …")
            return "\n".join(lines)

        if self.left:
            lines.append(f"l: {self.left._pretty(level + 1)}")
        if self.right:
            lines.append(f"r: {self.right._pretty(level + 1)}")

        return "\n".join(lines)

    def __str__(self):
        return self._pretty()

def is_red_nullable(node: Node | None):
    if node is None:
        return False 
    return node.color == "RED" 

def is_black_nullable(node: Node | None):
    if node is None:
        return True 
    return node.color == "BLACK"

class RBTree:
    # 1. Every node is RED or BLACK 
    # 2. Root node is BLACK 
    # 3. None nodes are BLACK 
    # 4. If a node is RED, both children are BLACK
    # 5. From any node, all simple paths down the leaf nodes have same number of black nodes

    def __init__(self):
        self.root = None

    def _rotate_right(self, pivot):
        left = pivot.left
        assert left is not None

        parent = pivot.parent
        side = pivot.side          

        # 1. move B to pivot.left
        pivot.left = left.right
        if left.right:
            left.right.parent = pivot
            left.right.side   = "LEFT"

        # 2. pivot becomes right child of left
        left.right  = pivot
        left.parent = parent
        pivot.parent = left
        pivot.side   = "RIGHT"

        # 3. hook left into its new parent position
        if parent is None:              # pivot was root
            self.root = left
            left.side = None
        elif side == "LEFT":
            parent.left = left
            left.side = "LEFT"
        else:                           # side == "RIGHT"
            parent.right = left
            left.side = "RIGHT"

    def _rotate_left(self, pivot):
        right = pivot.right
        assert right is not None

        parent    = pivot.parent
        old_side  = pivot.side          

        pivot.right = right.left
        if right.left:
            right.left.parent = pivot
            right.left.side   = "RIGHT"

        right.left  = pivot
        right.parent = parent
        pivot.parent = right
        pivot.side   = "LEFT"

        if parent is None:              
            self.root  = right
            right.side = None
        elif old_side == "LEFT":
            parent.left = right
            right.side  = "LEFT"
        else:                          
            parent.right = right
            right.side   = "RIGHT"

    def get(self, node: Node):
        if self.root is None:
            return Node

        else:
            head = self.root 

            # Insert
            while True:
                # Left
                if head.equals(node):
                    return node

                elif head.compare_for_right(node):

                    # Leaf
                    if head.left is None:
                        head.left = node 
                        node.parent = head
                        node.side = "LEFT"
                        break

                    # Continue
                    else:
                        head = head.left

                # Right
                else:

                    # Leaf
                    if head.right is None:
                        head.right = node 
                        node.parent = head
                        node.side = "RIGHT"
                        break

                    # Continue
                    else:
                        head = head.right



    def insert(self, node: Node):
        node.color = "RED"

        if self.root is None:
            self.root = node
            node.parent = None
            node.left = None 
            node.right = None
        else:
            head = self.root 

            # Insert
            while True:
                # Left
                if head.compare_for_right(node):

                    # Leaf
                    if head.left is None:
                        head.left = node 
                        node.parent = head
                        node.side = "LEFT"
                        break

                    # Continue
                    else:
                        head = head.left

                # Right
                else:

                    # Leaf
                    if head.right is None:
                        head.right = node 
                        node.parent = head
                        node.side = "RIGHT"
                        break

                    # Continue
                    else:
                        head = head.right

        # Fix Violations
        pivot = node

        while True:

            # Break condition (1)
            if pivot.parent is None:
                pivot.color = "BLACK"  # Root is black
                return

            # Break condition (2)
            if pivot.parent.color == "BLACK":
                # 2. pivot (RED) is not the root 
                # 4. pivot Only has black children
                # 5. Two black nodes that used to be here are just pushed down - no new black nodes
                pivot.color = "RED"      
                return

            # parent color is RED, so parent must have a parent 
            assert pivot.parent.parent is not None

            gparent: Node = pivot.parent.parent 
            uncle: Node | None = gparent.right if pivot.parent.side == "LEFT" else gparent.left

            # Break condition (3)
            if pivot.parent.color == "RED" and is_black_nullable(uncle):
                if pivot.side == pivot.parent.side:
                    u = pivot 
                    w = gparent

                    if pivot.side == "LEFT":
                        self._rotate_right(w)
                    else:
                        self._rotate_left(w)

                    u.color = "RED"
                    w.color = "RED"
                    u.parent.color = "BLACK"

                    return
                else:
                    # Capture temp nodes before reorg
                    v = pivot.parent 
                    w = gparent 
                    u = pivot 

                    if u.side == "LEFT":
                        self._rotate_right(v)
                        self._rotate_left(w)
                    else:
                        self._rotate_left(v)
                        self._rotate_right(w)


                    u.color = "BLACK"
                    w.color = "RED"
                    return

            if pivot.parent.color == "RED" and is_red_nullable(uncle):
                assert uncle is not None 

                # 2. pivot (RED) is not root
                # 4. pivot only has black children
                # 5. Pushed the issue up one pivot to deal with it later
                pivot.parent.color = "BLACK"
                uncle.color = "BLACK"
                pivot.color = "RED"

                pivot = gparent # Recursive step
                continue


    def __str__(self):
        return "========= RBTree\n" + str(self.root)


def verify_rb_tree(tree):
    root = tree.root
    assert root is not None, "tree is empty"
    assert root.color == "BLACK", "root must be black"
    assert root.parent is None, "root parent must be None"
    assert root.side is None, "root side must be None"

    def dfs(node):
        if node is None:
            return 1                

        assert node.color in ("RED", "BLACK"), f"invalid color at {node}"

        if node is not root:
            if node.side == "LEFT":
                assert node.parent.left is node, f"{node} claims LEFT but parent mismatch"
            elif node.side == "RIGHT":
                assert node.parent.right is node, f"{node} claims RIGHT but parent mismatch"
            else:
                raise AssertionError(f"{node} has side None (only root may)")

        if node.color == "RED":
            assert node.left is None or node.left.color == "BLACK", f"red violation at {node}"
            assert node.right is None or node.right.color == "BLACK", f"red violation at {node}"

        left_bh  = dfs(node.left)
        right_bh = dfs(node.right)
        assert left_bh == right_bh, f"black-height mismatch at {node}"

        return left_bh + (1 if node.color == "BLACK" else 0)

    dfs(root)              
    return True           

def test():
    t = RBTree()
    random.seed(11)

    for i in range(5000):
        r = random.randint(0, 10000)
        t.insert(Node(r))

    verify_rb_tree(t)

__all__ = ["Node", "RBTree", "verify_rb_tree", "test"]
__version__ = "0.0.2"

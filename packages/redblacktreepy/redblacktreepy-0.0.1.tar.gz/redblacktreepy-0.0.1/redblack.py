
from rbtree import Node, RBTree, test

if __name__ == '__main__':
    test()

    t = RBTree()

    t.insert(Node(5))
    t.insert(Node(9))
    t.insert(Node(1))
    t.insert(Node(100))
    t.insert(Node(11))
    t.insert(Node(11))
    t.insert(Node(2))

    print(t)

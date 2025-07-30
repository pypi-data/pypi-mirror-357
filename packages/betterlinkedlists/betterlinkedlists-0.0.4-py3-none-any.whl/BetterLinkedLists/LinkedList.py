from typing import Any

BEFORE = True
AFTER = False


class ItemNotFoundError(Exception):
    """
    Item does not appear in the LinkedList.
    """
    pass


class NodeType:
    def __init__(self):
        self.data = None
        self.next: NodeType = None
        self.before: NodeType = None


class LinkedListType:
    head: NodeType = None
    def find(self, item) -> NodeType: pass
    def findall(self, item) -> list[NodeType]: pass
    def append(self, item): pass
    def remove(self, item): pass
    def insert(self, data, where, value): pass


class Node(NodeType):
    def __init__(self, data):
        self.data = data
        self.next: Node = None

    
    def __str__(self):
        return str(self.data)


class LinkedList(LinkedListType):
    def __init__(self, *args):
        self.head = None
        if len(args) == 1 and isinstance(args[0], (dict, set, list, tuple, )):
            ls = list(args[0])
        else:
            ls = list(args)
        for item in ls:
            self.append(item)
        self._iter_node = None

    def append(self, data):
        new_node = Node(data) if not type(data) == Node else data
        if not self.head:
            self.head = new_node
            return
        last = self.head
        while last.next:
            last = last.next
        last.next = new_node


    def insert(self, data, where, value):
        '''
        where = True: insert before
        where = False: insert after
        '''
        try:
            self.find(value)
        except ItemNotFoundError:
            raise ItemNotFoundError(f"Cannot insert {'before' if where else 'after'} '{str(value)}': '{str(value)}' is not a member of the LinkedList.")
        new_node = Node(data) if not type(data) == Node else data

        if where:
            if isinstance(value, NodeType):
                if self.head == value:
                    new_node.next = self.head
                    self.head = new_node
                    return
                last = self.head
                while last.next:
                    if last.next == value:
                        break
                    last = last.next
                new_node.next = last.next
                last.next = new_node
            else:
                if self.head.data == value:
                    new_node.next = self.head
                    self.head = new_node
                    return
                last = self.head
                while last.next:
                    if last.next.data == value:
                        break
                    last = last.next
                new_node.next = last.next
                last.next = new_node
        else:
            if isinstance(value, NodeType):
                last = self.head
                while last.next:
                    if last == value:
                        break
                    last = last.next
                new_node.next = last.next
                last.next = new_node
            else:
                last = self.head
                while last.next:
                    if last.data == value:
                        break
                    last = last.next
                new_node.next = last.next
                last.next = new_node


    def remove(self, data: Any | Node):
        self.find(data)
        if type(data) == Node:
            for _ in range(len(self.findall(data))):
                if data == self.head:
                    self.head = self.head.next
                    continue
                last = self.head
                while last.next:
                    if data == last.next:
                        break
                    last = last.next
                last.next = last.next.next
            return
        for _ in range(len(self.findall(data))):
            if self.head.data == data:
                self.head = self.head.next
                continue
            last = self.head
            while last.next:
                if last.next.data == data:
                    break
                last = last.next
            last.next = last.next.next


    def __iter__(self):
        self._iter_node = self.head
        self._iter_started = False
        return self

    def __next__(self):
        if self._iter_node == None or (self._iter_node == self.head and self._iter_started):
            self._iter_node = self.head
            self._iter_started = False
            raise StopIteration
        data = self._iter_node.data
        self._iter_node = self._iter_node.next
        self._iter_started = True
        return data
    

    def __len__(self):
        count = 0
        for _ in self:
            count += 1
        return count
    

    def __getitem__(self, n):
        if n < 0:
            n = len(self) + n
        node = self.head
        idx = 0
        while node:
            if idx == n:
                return node
            node = node.next
            idx += 1
            if node == self.head or node is None:
                break
        raise IndexError("LinkedList index out of range")
    

    def find(self, value):
        node = self.head
        while node:
            if node.data == value and not isinstance(value, NodeType) or node == value:
                return node
            node = node.next
            if node == self.head or node is None:
                break
        raise ItemNotFoundError("The item was not found in the LinkedList.")
    

    def findall(self, value: Any | Node) -> list[Node]:
        self.find(value)
        nodes = []
        node = self.head
        while node:
            if node.data == value and not isinstance(value, NodeType):
                nodes.append(node)
            elif isinstance(value, NodeType) and node == value:
                nodes.append(node)
            node = node.next
            if node == self.head or node is None:
                break
        return nodes

    
    def __repr__(self):
        r = 'LinkedList{\n'
        node = self.head
        if node is None: return r + '    empty\n}'
        r += f'     (head) data: {node.data}, next: {node.next.data if not node.next.next == None else '(tail) ' + node.next.data}\n' if not node.next == None else f'    (tail) (head) data: {node.data}'
        while node:
            node = node.next
            if node == self.head or node is None:
                break
            r += f'     data: {node.data}, next: {node.next.data if not node.next.next == None else '(tail) ' + node.next.data}\n' if not node.next == None else f'     (tail) data: {node.data}'
        r += '\n}'
        return r
   
from LinkedList import Node, NodeType, LinkedList


class DoubleNode(Node):
    def __init__(self, data):
        super().__init__(data)
        self.before: DoubleNode = None
        self.next: DoubleNode = None


class DoubleLinkedList(LinkedList):
    def append(self, data):
        new_node = DoubleNode(data) if not type(data) == DoubleNode else data
        if not self.head:
            self.head = new_node
            return
        last = self.head
        while last.next:
            last = last.next
        last.next = new_node
        new_node.before = last


    def remove(self, data):
        if isinstance(data, NodeType):
            for _ in range(len(self.findall(data))):
                if self.head == data:
                    self.head.next.before = None
                    self.head = self.head.next
                    continue
                last = self.head
                while last.next:
                    if last.next == data:
                        break
                    last = last.next
                if last.next.next is not None: last.next.next.before = last
                last.next = last.next.next
            return
        for _ in range(len(self.findall(data))):
            if self.head.data == data:
                self.head.next.before = None
                self.head = self.head.next
                continue
            last = self.head
            while last.next:
                if last.next.data == data:
                    break
                last = last.next
            if last.next.next is not None: last.next.next.before = last
            last.next = last.next.next


    def insert(self, data, where, value):
        '''
        where = True: insert before
        where = False: insert after
        '''
        new_node = DoubleNode(data) if not type(data) == DoubleNode else data

        if where:
            if isinstance(value, NodeType):
                last = self.head
                while last.next:
                    if last.next == value:
                        break
                    last = last.next
                new_node.next = last.next
                new_node.next.before = new_node
                new_node.before = last
                last.next = new_node
            else:
                last = self.head
                while last.next:
                    if last.next.data == value:
                        break
                    last = last.next
                new_node.next = last.next
                new_node.next.before = new_node
                new_node.before = last
                last.next = new_node
        else:
            if isinstance(value, NodeType):
                last = self.head
                while last.next:
                    if last == value:
                        break
                    last = last.next
                new_node.next = last.next
                new_node.next.before = new_node
                new_node.before = last
                last.next = new_node
            else:
                last = self.head
                while last.next:
                    if last.data == value:
                        break
                    last = last.next
                new_node.next = last.next
                new_node.next.before = new_node
                new_node.before = last
                last.next = new_node


    def find(self, value) -> DoubleNode:
        return super().find(value)
    

    def findall(self, value) -> list[DoubleNode]:
        return super().findall(value)
    

    def __repr__(self):
        r = 'DoubleLinkedList{\n'
        node = self.head
        if node is None: return r + '    empty\n}'
        r += f'     (head) data: {node.data}, next: {node.next.data if not node.next.next == None else '(tail) ' + node.next.data}\n' if not node.next == None else f'    (tail) (head) data: {node.data}'
        while node:
            node = node.next
            if node == self.head or node is None:
                break
            r += f'     data: {node.data}, next: {node.next.data if not node.next.next == None else '(tail) ' + node.next.data}, before: {node.before.data if not node.before == self.head else '(head) ' + node.before.data}\n' if not node.next == None else f'     (tail) data: {node.data}, before: {node.before.data}'
        r += '\n}'
        return r

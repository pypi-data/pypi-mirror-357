from LinkedList import Node, NodeType, LinkedList
from typing import Any


class LoopedNode(Node):
    def __init__(self, data):
        super().__init__(data)
        self.next: LoopedNode = None


class LoopedLinkedList(LinkedList):
    def append(self, data):
        new_node = LoopedNode(data) if not type(data) == LoopedNode else data
        if not self.head:
            self.head = new_node
            new_node.next = self.head
            return
        last = self.head
        while not last.next is self.head:
            last = last.next
        last.next = new_node
        new_node.next = self.head

    
    def remove(self, data: Any | Node):
        if isinstance(data, NodeType):
            for _ in range(len(self.findall(data))):
                if self.head == data:
                    last = self.head
                    while last.next != self.head:
                        last = last.next
                    last.next = self.head.next
                    self.head = self.head.next
                    continue
                last = self.head
                while last.next:
                    if last.next == data:
                        break
                    last = last.next
                last.next = last.next.next
            return
        for _ in range(len(self.findall(data))):
            if self.head.data == data:
                last = self.head
                while last.next != self.head:
                    last = last.next
                last.next = self.head.next
                self.head = self.head.next
                continue
            last = self.head
            while last.next:
                if last.next.data == data:
                    break
                last = last.next
            last.next = last.next.next


    def insert(self, data, where, value):
        '''
        where = True: insert before
        where = False: insert after
        '''
        new_node = LoopedNode(data) if not type(data) == LoopedNode else data

        if where:
            if isinstance(value, NodeType):
                if self.head == value:
                    last = self.head
                    while last.next != self.head:
                        last = last.next
                    new_node.next = self.head
                    last.next = new_node
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
                    last = self.head
                    while last.next != self.head:
                        last = last.next
                    new_node.next = self.head
                    last.next = new_node
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


    def find(self, value) -> LoopedNode:
        return super().find(value)
    

    def findall(self, value) -> list[LoopedNode]:
        return super().findall(value)
    

    def __repr__(self):
        r = 'LoopedLinkedList{\n'
        node = self.head
        if node is None: return r + '    empty\n}'
        r += f'     (head) data: {node.data}, next: {node.next.data if not node.next.next == self.head else '(tail) ' + node.next.data}\n' if not node.next == self.head else f'    (tail) (head) data: {node.data}'
        node = node.next
        if node == self.head:
            r += '\n}'
            return r
        r += f'     data: {node.data}, next: {node.next.data if not node.next.next == self.head else '(tail) ' + node.next.data}\n' if not node.next == self.head else f'     (tail) data: {node.data}, next: (head) {node.next.data}'
        while node != self.head:
            node = node.next
            if node == self.head or node is None:
                break
            r += f'     data: {node.data}, next: {node.next.data}\n' if not node.next == self.head else f'     (tail) data: {node.data}, next: (head) {node.next.data}'
        r += '\n}'
        return r

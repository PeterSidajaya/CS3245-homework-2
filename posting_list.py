class posting_list:
    def __init__(self, val):
        self.val = val
        self.next = None
        self.has_skip = False
        self.skip = None
    
    def add_skip(self, space):
        pointer = self
        for i in range(space):
            pointer = pointer.next
        self.skip = pointer
        self.has_skip = True

class list_node:
    def __init__(self):
        self.size = 0
        self.head = None
        self.tail = None
    
    def insert_head(self, val):
        new_node = posting_list(val)
        new_node.next = self.head
        self.head = new_node.next

    def insert_tail(self, val):
        new_node = posting_list(val)
        self.tail.next = new_node
        self.tail = new_node
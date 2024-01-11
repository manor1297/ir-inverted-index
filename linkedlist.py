import math


class Node:

    def __init__(self, value=None, next=None, skip=None, tf=1.0, token_num=None, tfidf=None):
        """ Class to define the structure of each node in a linked list (postings list).
            Value: document id, Next: Pointer to the next node
            Add more parameters if needed.
            Hint: You may want to define skip pointers & appropriate score calculation here"""
        self.value = value
        self.next = next
        self.skip = skip
        self.tf = tf
        self.token_num = token_num
        self.tfidf = tfidf


class LinkedList:
    """ Class to define a linked list (postings list). Each element in the linked list is of the type 'Node'
        Each term in the inverted index has an associated linked list object.
        Feel free to add additional functions to this class."""

    def __init__(self):
        self.start_node = None
        self.end_node = None
        self.length, self.n_skips, self.idf = 0, 0, 0.0
        self.skip_length = None

    def traverse_list(self):
        traversal = []
        if self.start_node is None:
            return
        else:
            """ Write logic to traverse the linked list.
                To be implemented."""
            n = self.start_node
            # Start traversal from head, and go on till you reach None
            while n is not None:
                traversal.append(n.value)
                n = n.next
            # raise NotImplementedError
            return traversal

    def traverse_skips(self):
        traversal = []
        if self.start_node is None:
            return
        else:
            """ Write logic to traverse the linked list using skip pointers.
                To be implemented."""
            n = self.start_node
            # Start traversal from head, and go on till you reach None
            while n is not None:
                traversal.append(n.value)
                n = n.skip
            # raise NotImplementedError
            return traversal

    def traverse_list_tfidf(self):
        traversal = []
        if self.start_node is None:
            return
        else:
            """ Write logic to traverse the linked list.
                To be implemented."""
            n = self.start_node
            # Start traversal from head, and go on till you reach None
            while n is not None:
                traversal.append([n.value, n.tfidf])
                n = n.next
            # raise NotImplementedError
            return traversal

    def add_skip_connections(self):
        n_skips = math.floor(math.sqrt(self.length))
        if n_skips * n_skips == self.length:
            n_skips = n_skips - 1
        """ Write logic to add skip pointers to the linked list. 
            This function does not return anything.
            To be implemented."""
        btwn = round(math.sqrt(self.length), 0)
        if self.start_node is None:
            return
        else:
            n = self.start_node
            t = self.start_node
            flag = btwn - 1
            while n is not None:
                n = n.next
                flag -= 1
                if flag == 0:
                    if n is not None:
                        t.skip = n.next
                        t = n.next
                    flag = btwn
        # raise NotImplementedError

    def insert_at_end(self, value, token_num=None, tfidf=None):
        """ Write logic to add new elements to the linked list.
            Insert the element at an appropriate position, such that elements to the left are lower than the inserted
            element, and elements to the right are greater than the inserted element.
            To be implemented. """
        new_node = Node(value=value, token_num=token_num, tfidf=tfidf)
        n = self.start_node
        self.length += 1

        if self.start_node is None:
            self.start_node = new_node
            self.end_node = new_node
            return

        elif self.start_node.value >= value:
            self.start_node = new_node
            self.start_node.next = n
            return

        elif self.end_node.value <= value:
            self.end_node.next = new_node
            self.end_node = new_node
            return

        else:
            while n.value < value < self.end_node.value and n.next is not None:
                n = n.next

            m = self.start_node
            while m.next != n and m.next is not None:
                m = m.next
            m.next = new_node
            new_node.next = n
            return
        # raise NotImplementedError

    def increment_tf(self, value):
        if self.start_node is None:
            return
        else:
            n = self.start_node
            # Start traversal from head, and go on till you reach None
            while n is not None:
                if value == n.value:
                    n.tf += 1
                    break
                else:
                    n = n.next
            # raise NotImplementedError
            return

    def score(self, doc_num):
        self.idf = doc_num / self.length
        if self.start_node is None:
            return
        else:
            n = self.start_node
            # Start traversal from head, and go on till you reach None
            while n is not None:
                n.tfidf = self.idf * (n.tf / n.token_num)
                n.tfidf = round(n.tfidf, 3)
                n = n.next
            # raise NotImplementedError
            return

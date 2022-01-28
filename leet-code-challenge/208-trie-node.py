class TrieNode:
    def __init__(self, char: str = ""):
        self.char = char
        self.children = {}
        self.key = False

class Trie:

    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        node = self.root
        for idx, c in enumerate(word):
            if c not in node.children:
                node.children[c] = TrieNode(c)
            node = node.children[c]
        
        node.key = True
                
                
                

    def search(self, word: str) -> bool:
        node = self.root
        for idx, c in enumerate(word):
            if c not in node.children:
                return False
            node = node.children[c]
        if node.key is True:
            return True
        else:
            return False
        

    def startsWith(self, prefix: str) -> bool:
        node = self.root
        for idx, c in enumerate(prefix):
            if c not in node.children:
                return False
            node = node.children[c]
        return True


# Your Trie object will be instantiated and called as such:
# obj = Trie()
# obj.insert(word)
# param_2 = obj.search(word)
# param_3 = obj.startsWith(prefix)
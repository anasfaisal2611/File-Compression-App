import heapq

# Class to represent huffman tree
class Node:
	def __init__(self, x,freq):
		self.data = x
		self.left = None
		self.right = None
		self.freq=freq

	def __lt__(self, other):
		return self.freq < other.freq

# Function to traverse tree in preorder
# manner and push the huffman representation
# of each character.
def preOrder(root, code_dict, curr):
	if root is None:
		return

	# Leaf node represents a character.
	if root.left is None and root.right is None:
		code_dict[root.data]=curr or "0"

		return


	preOrder(root.left, code_dict, curr + '0')
	preOrder(root.right, code_dict, curr + '1')

def huffmanCodes(s, freq):
	# Code here
	n = len(s)

	# Min heap for node class.
	pq = []
	for i in range(n):
		tmp = Node(s[i],freq[i])
		heapq.heappush(pq, tmp)

	# Construct huffman tree.
	while len(pq) >= 2:
		# Left node
		l = heapq.heappop(pq)

		# Right node
		r = heapq.heappop(pq)

		newNode = Node(None,l.freq+ r.freq)
		newNode.left = l
		newNode.right = r

		heapq.heappush(pq, newNode)

	root = heapq.heappop(pq)
	code_dict={}
	preOrder(root, code_dict, "")
	return code_dict

if __name__ == "__main__":
	s = "abcdef"
	freq = [5, 9, 12, 13, 16, 45]
	ans = huffmanCodes(s, freq)
	for code in ans:
		print(code, end=" ")

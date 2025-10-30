import hashlib

def hash_pair(a, b):
    """
    Hash a pair of strings together
    Args:
        a: First hash string
        b: Second hash string
    Returns:
        str: Combined hash
    """
    return hashlib.sha256((a + b).encode('utf-8')).hexdigest()

def merkle_root(hashes):
    """
    Compute Merkle root from a list of hashes
    Args:
        hashes: List of hash strings
    Returns:
        str: Merkle root hash
    """
    if not hashes:
        return ''
    
    if len(hashes) == 1:
        return hashes[0]
    
    layer = hashes[:]
    
    while len(layer) > 1:
        # If odd number of hashes, duplicate the last one
        if len(layer) % 2 == 1:
            layer.append(layer[-1])
        
        # Hash pairs
        layer = [hash_pair(layer[i], layer[i+1]) 
                for i in range(0, len(layer), 2)]
    
    return layer[0]

class MerkleTree:
    """Merkle Tree implementation for batch record anchoring"""
    
    def __init__(self):
        self.leaves = []
        self.root = None
    
    def add_leaf(self, leaf_hash):
        """Add a leaf hash to the tree"""
        self.leaves.append(leaf_hash)
        self.root = None  # Invalidate root
    
    def add_leaves(self, leaf_hashes):
        """Add multiple leaf hashes"""
        self.leaves.extend(leaf_hashes)
        self.root = None
    
    def compute_root(self):
        """Compute and cache the Merkle root"""
        if not self.leaves:
            return None
        self.root = merkle_root(self.leaves)
        return self.root
    
    def get_root(self):
        """Get the cached root or compute if needed"""
        if self.root is None:
            return self.compute_root()
        return self.root
    
    def get_proof(self, leaf_index):
        """
        Generate Merkle proof for a specific leaf
        Args:
            leaf_index: Index of the leaf
        Returns:
            list: List of (hash, direction) tuples for the proof path
        """
        if leaf_index >= len(self.leaves):
            return None
        
        proof = []
        layer = self.leaves[:]
        index = leaf_index
        
        while len(layer) > 1:
            if len(layer) % 2 == 1:
                layer.append(layer[-1])
            
            # Determine sibling
            if index % 2 == 0:
                # Current is left, sibling is right
                sibling_index = index + 1
                direction = 'right'
            else:
                # Current is right, sibling is left
                sibling_index = index - 1
                direction = 'left'
            
            if sibling_index < len(layer):
                proof.append((layer[sibling_index], direction))
            
            # Move to next layer
            layer = [hash_pair(layer[i], layer[i+1]) 
                    for i in range(0, len(layer), 2)]
            index = index // 2
        
        return proof
    
    def verify_proof(self, leaf_hash, proof, root):
        """
        Verify a Merkle proof
        Args:
            leaf_hash: The leaf hash to verify
            proof: List of (hash, direction) tuples
            root: Expected Merkle root
        Returns:
            bool: True if proof is valid
        """
        current = leaf_hash
        
        for sibling_hash, direction in proof:
            if direction == 'right':
                current = hash_pair(current, sibling_hash)
            else:
                current = hash_pair(sibling_hash, current)
        
        return current == root
    
    def reset(self):
        """Reset the tree"""
        self.leaves = []
        self.root = None
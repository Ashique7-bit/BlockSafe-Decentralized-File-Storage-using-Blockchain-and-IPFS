import hashlib
import json
import time
from datetime import datetime
from config import Config

class Block:
    def __init__(self, index, timestamp, data, previous_hash, nonce=0):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.calculate_hash()
    
    def calculate_hash(self):
        block_string = json.dumps({
            "index": self.index,
            "timestamp": str(self.timestamp),
            "data": self.data,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def to_dict(self):
        return {
            "index": self.index,
            "timestamp": str(self.timestamp),
            "data": self.data,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "hash": self.hash
        }

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.difficulty = Config.DIFFICULTY
    
    def create_genesis_block(self):
        return Block(0, datetime.now(), {"message": "Genesis Block"}, "0")
    
    def get_latest_block(self):
        return self.chain[-1]
    
    def add_block(self, new_block):
        new_block.previous_hash = self.get_latest_block().hash
        new_block.hash = new_block.calculate_hash()
        self.mine_block(new_block)
        self.chain.append(new_block)
        return new_block
    
    def mine_block(self, block):
        target = "0" * self.difficulty
        while block.hash[:self.difficulty] != target:
            block.nonce += 1
            block.hash = block.calculate_hash()
    
    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            
            if current_block.hash != current_block.calculate_hash():
                return False
            
            if current_block.previous_hash != previous_block.hash:
                return False
            
            if current_block.hash[:self.difficulty] != "0" * self.difficulty:
                return False
        
        return True
    
    def validate_chain(self):
        errors = []
        details = {
            'total_blocks': len(self.chain),
            'valid_blocks': 0,
            'invalid_blocks': 0,
            'block_details': []
        }
        
        # Check genesis block
        genesis = self.chain[0]
        if genesis.index != 0 or genesis.previous_hash != "0":
            errors.append("Genesis block is invalid")
            details['block_details'].append({
                'block_index': 0,
                'status': 'Invalid',
                'issues': ['Genesis block structure is invalid']
            })
        else:
            details['valid_blocks'] += 1
            details['block_details'].append({
                'block_index': 0,
                'status': 'Valid',
                'issues': []
            })
        
        # Check subsequent blocks
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            block_issues = []
            
            if current_block.index != previous_block.index + 1:
                block_issues.append(f"Block index mismatch: Expected {previous_block.index + 1}, got {current_block.index}")
            
            if current_block.previous_hash != previous_block.hash:
                block_issues.append("Previous hash doesn't match the actual previous block's hash")
            
            if current_block.hash != current_block.calculate_hash():
                block_issues.append("Block's hash doesn't match its calculated hash")
            
            if current_block.hash[:self.difficulty] != "0" * self.difficulty:
                block_issues.append(f"Proof-of-work invalid: Hash doesn't start with {self.difficulty} zeros")
            
            if block_issues:
                errors.append(f"Block {current_block.index} has issues")
                details['invalid_blocks'] += 1
                details['block_details'].append({
                    'block_index': current_block.index,
                    'status': 'Invalid',
                    'issues': block_issues
                })
            else:
                details['valid_blocks'] += 1
                details['block_details'].append({
                    'block_index': current_block.index,
                    'status': 'Valid',
                    'issues': []
                })
        
        is_valid = len(errors) == 0
        return is_valid, errors, details
    
    def get_file_by_hash(self, ipfs_hash):
        for block in self.chain:
            if 'ipfs_hash' in block.data and block.data['ipfs_hash'] == ipfs_hash:
                return block.data
        return None
    
    def get_all_files(self):
        files = []
        for block in self.chain:
            if 'filename' in block.data:
                files.append(block.data)
        return files
    
    def to_dict(self):
        return [block.to_dict() for block in self.chain]
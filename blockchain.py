import json
import time
import hashlib
import settings

# TODO: Fix difficulty calculation algorithm to use last 10 blocks for average
# TODO: Add mining reward transaction to new block
class Block:
    def __init__(self, index, timestamp, data, previous_hash, proof, difficulty):
        self.version = settings.VERSION
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.proof = proof
        self.difficulty = difficulty

    @property
    def hash(self):
        sha = hashlib.sha256()
        sha.update(str(self.version).encode('utf-8') +
                   str(self.index).encode('utf-8') +
                   str(self.timestamp).encode('utf-8') +
                   str(self.data).encode('utf-8') +
                   str(self.previous_hash).encode('utf-8') +
                   str(self.proof).encode('utf-8') + 
                   str(self.difficulty).encode('utf-8'))
        return sha.hexdigest()
    
    def dumb_block_data(self):
        block = {
            'version': self.version,
            'index': self.index,
            'timestamp': self.timestamp,
            'data': self.data,
            'previous_hash': self.previous_hash,
            'proof': self.proof,
            'difficulty': self.difficulty
        }
        return json.dumps(block).encode()
    
    def __str__(self):
        return f"## Block Object ##\nVersion: {self.version}\nIndex: {self.index}\nTimestamp: {self.timestamp}\nData: {self.data}\nPrevious_hash: {self.previous_hash}\nProof: {self.proof}\nDifficulty: {self.difficulty}\nHash: {self.hash}\n"
        
class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        # Create the genesis block
        self.new_block(previous_hash=0, proof=0, difficulty=settings.BLOCK_INIT_DIFFICULTY)

    def new_block(self, proof, previous_hash, difficulty) -> Block:
        """
        Create a new Block in the Blockchain

        :param proof: The proof given by the Proof of Work algorithm to confirm the block
        :param previous_hash: Hash of previous Block
        :return: New Block
        """
        block = Block(len(self.chain) + 1, 
                        time.time(), 
                        self.current_transactions, 
                        previous_hash, proof,difficulty)

        # Reset the current list of transactions
        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount) -> int:
        """
        Creates a new transaction to go into the next mined Block

        :param sender: Address of the Sender
        :param recipient: Address of the Recipient
        :param amount: Amount
        :return: The index of the Block that will hold this transaction
        """
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })

        return self.last_block.index + 1
    
    @property
    def last_block(self) -> Block:
        return self.chain[-1]
        
    def proof_of_work(self, last_block, difficulty, proof_change=1) -> int:
        """
        Simple Proof of Work Algorithm:
            - Find a number p that the hash of the current block contains leading difficulty * zeroes
         
        :param last_block: Block Object of last block
        :param difficulty: Difficulty of the proof
        :return: <int>
        """
        proof = 0
        while self.valid_proof(proof, last_block, difficulty) is False:
            proof += proof_change
        return proof
    
    @staticmethod
    def valid_proof(proof, last_block, difficulty) -> bool:
        guess = f'{last_block.hash}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:difficulty] == '0' * difficulty
    
    @staticmethod
    def check_validity(block: Block, prev_block: Block) -> bool:
        if prev_block.index + 1 != block.index:
            return False

        elif prev_block.hash != block.previous_hash:
            return False

        elif not Blockchain.valid_proof(block.proof, prev_block.proof):
            return False

        elif block.timestamp <= prev_block.timestamp:
            return False
        
        elif block.hash != block.calculate_hash():
            return False
        
        return True
    
    @staticmethod
    def calculate_difficulty(chain, current_difficulty) -> int:
        """
        Calculate the difficulty of the next block to mine
        """
        # if the 2 last blocks were mined in less than BLOCK_TIME seconds, increase the difficulty  
        if chain[-1].timestamp - chain[-2].timestamp < settings.BLOCK_TIME:
            return current_difficulty + 1
        # if the 2 last blocks were mined in more than BLOCK_TIME seconds, decrease the difficulty
        elif chain[-1].timestamp - chain[-2].timestamp > settings.BLOCK_TIME:
            return current_difficulty - 1
        # if the 2 last blocks were mined in exactly BLOCK_TIME seconds, keep the difficulty
        else:
            return current_difficulty
    
    @staticmethod
    def calculate_reward(chain) -> int:
        """
        Calculate the reward of the next block to mine
        """
        block_reward = settings.BLOCK_INIT_REWARD / (2 ** (chain[-1].index / settings.HALVING_INTERVAL))
        return block_reward
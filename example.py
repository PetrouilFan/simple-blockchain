import blockchain
import time
import settings
# Create a blockchain
bc = blockchain.Blockchain()
# Get Initial difficulty
difficulty = settings.BLOCK_INIT_DIFFICULTY
mine_times = []


try:
    while True:
        # Start timer
        start_time = time.time()
        # Add a transaction
        bc.new_transaction('sender', 'receiver', 1)
        # Mine a block
        proof = bc.proof_of_work(bc.last_block, difficulty)
        # Add the block to the chain
        bc.new_block(proof, bc.last_block.hash, difficulty)
        # Calculate the new difficulty
        difficulty = blockchain.Blockchain.calculate_difficulty(bc.chain, difficulty)
        # Add the time it took to mine the block to the list
        mine_times.append(time.time() - start_time)
        # Print the results
        print(f'Block {bc.last_block.index} mined in {time.time() - start_time} seconds')
        print(f'Block hash: {bc.last_block.hash}')
        print(f'New Block difficulty: {difficulty}')
except KeyboardInterrupt:
    # Print the average block time
    print(f'Average block time: {sum(mine_times) / len(mine_times)}')


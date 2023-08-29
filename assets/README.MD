# Instruction:
To test the program, simply replace txs file that contains all the transactions and run node.py. Or run generate tx.py to create a new txs file. 
# Task checklist:
* Authentic transactions that are resistant to theft      Done (transaction.py/node.py)
* Open competition amongst nodes to validate transactions     Done (node.py)
* Detection of double spending        Done (blockchain.py/node.py)
* Use of proof-of-work to raise the cost of running attacks against the network       Done (blockchain.py/pow.py)
* Detection of and reaction to forks in the chain     Done (blockchain.py/node.py)
* Three check: Verify the proof-of-work/Verify the prev hash/Validate the transaction in the block        Done(blockchain.py)
# Notes:
* The first transaction in the transaction pool is the one in genesis block and genesis block is always valid and automatically added to the blockchain. Thus, it has to be valid in its own way when testing. 
* I did not test malicious nodes but the mechanisms should be sufficient.

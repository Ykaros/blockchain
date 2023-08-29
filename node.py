import json
import threading
import queue
import random
from time import sleep as sleep
from blockchain import Blockchain
from block import Block
from transaction import Transaction


class Node(threading.Thread):
    def __init__(self, thread_idx, genesis_block):
        threading.Thread.__init__(self)
        self.idx = thread_idx
        # node queue to store blockchain for broadcasting
        self.q = queue.Queue()

        # valid tx on chain or invalid ones off chain
        self.chained_tx = set()
        self.invalidTx = set()

        # local view
        self.blockchain = Blockchain(genesis_block)

    # validation check of current tx from pool
    def tx_to_chain(self):
        global unverifiedTxs

        # assume the genesis is always valid
        self.chained_tx.add(self.blockchain.chain[0].tx.number)
        # check the rest ones
        for (tx_number_unverified, tx_unverified) in list(unverifiedTxs.items()):
            # valid tx not on chain yet
            if tx_number_unverified not in self.chained_tx and tx_number_unverified not in self.invalidTx:

                tx = Transaction(ipt=tx_unverified["input"], opt=tx_unverified["output"],
                                 signature=tx_unverified["sig"].encode("utf-8"))

                # check if transaction itself is validly structured
                try:
                    tx.validate()
                    print(tx_number_unverified + " is validly structured")
                except:
                    # invalid
                    self.invalidTx.add(tx_number_unverified)
                    print(tx_number_unverified + " is not validly structured")
                    # receive blockchain from other nodes
                    continue

                # check if transaction input number exists
                for i in tx.input:
                    if i["number"] not in self.chained_tx:
                        print("Invalid Input")
                        self.invalidTx.add(tx_number_unverified)
                        break

                # add transaction to chain if no double spending exists
                try:
                    self.blockchain.to_chain(tx)
                    self.chained_tx.add(tx.number)
                    print("Node " + str(self.idx) + " mined block " + str(len(self.blockchain.chain)))
                    self.broadcast_chain()
                except:
                    # invalid
                    self.invalidTx.add(tx_number_unverified)
                    print("Double spending detected on", tx_number_unverified)
                    # receive blockchain from other nodes
                    continue
            # print(self.invalidTx)

    # receive blockchain from others and verify it
    def receive_chain(self):
        received_chain = self.q.get()
        print("Node " + str(self.idx) + " received a blockchain")
        # print("The blockchain is ", received_chain.print())
        if len(received_chain.chain) > len(self.blockchain.chain):
            if self.blockchain.validate(received_chain):
                # print("XXXXXXXXXXXXXXXXXXXXXXXXXXX")
                self.chained_tx = set()
                self.blockchain = received_chain
                for block in self.blockchain.chain:
                    self.chained_tx.add(block.tx.number)

    # send blockchain to others' queue
    def broadcast_chain(self):
        print("Node " + str(self.idx) + " sent a blockchain")
        global nodes
        for id, node in nodes.items():
            if id != self.idx:
                node.q.put(self.blockchain)

    def run(self):
        try:
            print("Node " + str(self.idx) + " is running now")
            while True:
                sleep(random.uniform(0.141, 0.42))
                # check message
                while not self.q.empty():
                    self.receive_chain()
                # work on own chain
                self.tx_to_chain()
                global TERMINATE_THREADS
                if TERMINATE_THREADS:
                    break
        finally:
            print("Node " + str(self.idx) + " stopped")

    def print(self):
        print("Node " + str(self.idx) + " finalized a blockchain")
        self.blockchain.print()


# create all nodes
def initialize_nodes(num_nodes, genesis_block):
    global nodes
    nodes_idx = set()
    # assign an index to each node
    for i in range(1, num_nodes + 1):
        key = str(i)
        nodes_idx.add(key)
        # Create node in thread
        nodes[key] = Node(key, genesis_block)
        # Start it
        nodes[key].start()
    # print(nodes_idx)
    return nodes_idx


# these variables are globally accessible to all nodes
TERMINATE_THREADS = False
nodes = {}
unverifiedTxs = {}

# Driver Program
if __name__ == "__main__":

    with open("txs") as json_file:
        txs = json.loads(json_file.read())
    for tx in txs:
        # sleep(random.uniform(0, 1))
        unverifiedTxs[tx['number']] = tx
        # print(Transaction(ipt=tx["input"], opt=tx["output"], signature=tx["sig"].encode("utf-8")))

    # assume genesis block is always valid and automatically verified
    genesis = Block(tx=Transaction(ipt=txs[0]["input"], opt=txs[0]["output"], signature=txs[0]["sig"].encode("utf-8")))
    unverifiedTxs.pop(txs[0]["number"])

    # simulate all honest nodes
    honest_nodes = initialize_nodes(10, genesis)

    # terminating rule: consensus
    while True:
        sizes = {len(nodes[id].chained_tx) for id in honest_nodes}
        if len(sizes) == 1:
            TERMINATE_THREADS = True
            break
        print("The total size of blockchain is ", sizes)

    # terminate all nodes and show blockchain by each although the blockchains are identical
    for id, node in nodes.items():
        if id in honest_nodes:
            node.print()
        node.join()

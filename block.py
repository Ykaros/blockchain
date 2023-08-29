from transaction import Transaction
from hashlib import sha256 as H


class Block:
    def __init__(self, tx=Transaction(), previous_hash="0"*64):
        self.tx = tx
        self.prev = previous_hash
        self.nonce = "Is There Anybody Out There?"
        self.pow = self.hashing()
        # self.target_pow = b"0x07FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF"

    # create number for block by previous block number, tx and nonce
    def hashing(self):
        h = H()
        h.update(str(self.prev).encode('utf-8'))
        h.update(str(self.tx).encode('utf-8'))
        h.update(str(self.nonce).encode('utf-8'))
        return h.hexdigest()

    # check if the block is valid
    def validate(self):
        # verifying number of block
        if self.hashing() != self.pow:
            print("Wrong number!")
            return False
        return True

    # update nonce to the block to validate the block
    def update(self, nonce):
        # self.tx = tx
        # self.prev = previous_hash
        self.nonce = nonce
        self.pow = self.hashing()

    # show details of the block
    def print(self, pad=""):
        print(pad, "##########---------- Block Details ----------##########")
        print(pad, "[@] Prev Block Hash : {}".format(self.prev))
        print(pad, "[@] Hash : {}".format(self.pow))
        print(pad, "[@] Nonce : {}".format(self.nonce))
        self.tx.print()


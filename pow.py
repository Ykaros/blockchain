import sys
from block import Block


# nonce for work
class Work:
    def __init__(self, nonce, _hash):
        self.nonce = nonce
        self.hash = _hash


# proof-of-work
class Proof:
    def __init__(self, block):
        self.block = block
        # difficulty factor
        self.target_pow = "07FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF"

    def get_hash(self, nonce):
        self.block.update(nonce)
        return self.block.hashing()

    def run(self):
        for nonce in range(42, sys.maxsize):  # 2^63-1
            _hash = self.get_hash(nonce)
            if _hash < self.target_pow:
                return Work(nonce, _hash)



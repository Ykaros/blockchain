from block import Block
from pow import *
from hashlib import sha256 as H


class Blockchain:
    def __init__(self, genesis_block):
        self.chain = [genesis_block]

        # UTXO index list
        self.utxo = {}
        for output in genesis_block.tx.output:
            key = self.hash_tx_receiver(genesis_block.tx.number.encode("utf-8"), output['pubkey'].encode("utf-8"))
            self.utxo[key] = 0

    # record information about tx number and receiver
    def hash_tx_receiver(self, tx_number, receiver_pubkey):
        h = H()
        h.update(tx_number)
        h.update(receiver_pubkey)
        return h.hexdigest()
    #
    # def tx_validation(blockchain, block):
    #
    # create block for tx and add it into the chain
    def to_chain(self, tx):
        for tx_input in tx.input:

            # previous tx number
            prev_tx = tx_input['number']
            key = self.hash_tx_receiver(prev_tx.encode('utf-8'), tx.input[0]['output']['pubkey'].encode('utf-8'))

            # no source for current sender
            if key not in self.utxo:
                raise Exception

            # find the blocks that send payments to sender
            prev_block_idx = self.utxo[key]
            prev_block = self.chain[prev_block_idx]

            # confirm the transaction details (current sender is the previous receiver and the amount matches)
            prev_tx_output = prev_block.tx.output
            confirmed = False
            for tx_output in prev_tx_output:
                if tx_output['pubkey'] == tx_input['output']['pubkey'] and tx_output['value'] == tx_input['output']['value']:
                    confirmed = True
            if not confirmed:
                raise Exception

            # remove outdated UTXO of sender
            del self.utxo[key]

        # add the current receiver to UTXO index list
        for tx_output in tx.output:
            updated_key = self.hash_tx_receiver(tx.number.encode("utf-8"), tx_output['pubkey'].encode("utf-8"))
            self.utxo[updated_key] = len(self.chain)

        # hash of previous block
        prev_hash = self.chain[len(self.chain) - 1].pow
        # create block and finish PoW on it
        current_block = Block(tx, prev_hash)
        work = Proof(current_block).run()
        # update nonce
        current_block.update(work.nonce)
        # add it to chain
        self.chain.append(current_block)

    # check if the received chain is valid
    def validate(self, chain):
        if chain.chain[0].pow != self.chain[0].pow:
            print("Wrong GENESIS BLOCK!")
            return False

        utxo = {}
        for output in self.chain[0].tx.output:
            key = self.hash_tx_receiver(self.chain[0].tx.number.encode("utf-8"),
                                        output['pubkey'].encode("utf-8"))
            utxo[key] = 0
        # print("Chain length", len(chain.chain))
        for pos, block in enumerate(chain.chain[1:]):

            # obtain pow according to the block details
            h = H()
            h.update(str(block.prev).encode('utf-8'))
            h.update(str(block.tx).encode('utf-8'))
            h.update(str(block.nonce).encode('utf-8'))
            pow = h.hexdigest()

            # PoW check (invalid or forged PoW)
            if pow > "07FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF" or block.pow != pow:
                print("Wrong PoW!")
                return False

            # prev_hash check
            if block.prev != chain.chain[pos].pow:
                print("Wrong previous block!")
                return False

            # tx validation check
            for tx_input in block.tx.input:
                # previous tx number
                prev_tx = tx_input['number']
                key = self.hash_tx_receiver(prev_tx.encode('utf-8'), block.tx.input[0]['output']['pubkey'].encode('utf-8'))

                # no source for current sender
                if key not in utxo:
                    return False

                # find the blocks that send payments to sender
                prev_block_idx = utxo[key]
                prev_block = chain.chain[prev_block_idx]

                # confirm the transaction details (current sender is the previous receiver and the amount matches)
                prev_tx_output = prev_block.tx.output
                confirmed = False
                for tx_output in prev_tx_output:
                    if tx_output['pubkey'] == tx_input['output']['pubkey'] and tx_output['value'] == tx_input['output']['value']:
                        confirmed = True
                if not confirmed:
                    return False

                # remove outdated UTXO of sender
                del utxo[key]

            # add the current receiver to UTXO index list
            for tx_output in block.tx.output:
                updated_key = self.hash_tx_receiver(block.tx.number.encode("utf-8"), tx_output['pubkey'].encode("utf-8"))
                utxo[updated_key] = pos + 1

        return True

    def print(self, pad=""):
        print(pad, "##########---------- Blockchain Details ----------##########")
        print(pad, "[@] Genesis Block : {}".format(self.chain[0].pow))
        print(pad, "[@] Blockchain Length : {}".format(len(self.chain)))
        # print(pad, "[@] Amount : {}".format(self.output["value"]))
        print(pad, "[@] The rest of the blocks :")
        for pos, block in enumerate(self.chain[1:]):
            print(pad, "[@] PoW of Block {} : {}".format(pos+2, block.pow))
            print(pad, "[@] Transaction Number : {}".format(block.tx.number))
        print()

from nacl.signing import SigningKey
from nacl.signing import VerifyKey
from nacl.encoding import HexEncoder
import json
from hashlib import sha256 as H


class Transaction:
    def __init__(self, ipt=[], opt=[], signature=b"I am VALID"):
        self.input = ipt
        self.output = opt
        self.sig = signature.decode()
        self.number = self.create_hash()

    # create number for each tx by input, output and sig
    def create_hash(self):
        h = H()
        h.update(json.dumps(self.input).encode('utf-8'))
        h.update(json.dumps(self.output).encode('utf-8'))
        h.update(self.sig.encode())
        return h.hexdigest()

    # check if transaction is valid
    def validate(self):

        # missing values
        if (not self.input) or (not self.output) or (not self.sig) or (not self.number):
            print("Missing Values!")
            raise Exception

        # wrong number
        if self.number != self.create_hash():
            print("Wrong Number!")
            raise Exception

        # input and output sum does not match
        sum_i = 0
        sum_o = 0
        for i in self.input:
            sum_i += i["output"]["value"]
        for o in self.output:
            sum_o += o["value"]
        if sum_i != sum_o:
            print("Input and output sum does not match!")
            raise Exception

        # wrong sig
        vk = VerifyKey(self.input[0]['output']['pubkey'].encode('utf-8'), encoder=HexEncoder)
        try:
            vk.verify(self.sig, encoder=HexEncoder)
        except:
            print("Wrong Signature!")
            raise Exception

    # show details of tx
    def print(self, pad=""):
        print(pad, "##########---------- Tx Details ----------##########")
        print(pad, "[@] Transaction Hash: {}".format(self.number))
        print(pad, "[@] Sender PubKey : {}".format(self.input[0]["output"]["pubkey"]))
        # print(pad, "[@] Amount : {}".format(self.output["value"]))
        # print(pad, "[@] PubKey : {}".format(self.output["pubkey"]))
        print(pad, "[@] Signature : {}".format(self.sig))
        print()

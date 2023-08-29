from transaction import *
from nacl.encoding import HexEncoder
from nacl.signing import SigningKey
from nacl.signing import VerifyKey


def keygen():
    signing_key = SigningKey.generate()
    return (signing_key, signing_key.verify_key.encode(encoder=HexEncoder).decode('utf-8'))


def create_signature(ipt, opt, signing_key):
    tx_data = json.dumps(ipt).encode('utf-8') + json.dumps(opt).encode('utf-8')
    return signing_key.sign(tx_data, encoder=HexEncoder)


# user list
users = ['PF', 'RH', 'O', 'C', 'KC', 'VU', 'RS', 'LZ', 'GNR', 'PIL']
user_keys = {}
# assign key pairs to each user
for u in users:
    user_keys[u] = keygen()

# initial value is 42
value = 42
tx_pool = []
# first transaction to first user
genesis_tx = Transaction(opt=[{"value": value, "pubkey": user_keys['PF'][1]}])
tx_pool.append(genesis_tx)
prev_tx_h = genesis_tx.number

# 15 valid tx
for i in range(15):
    ipt = []
    opt = []
    sender = users[i % len(users)]
    receiver = users[(i + 1) % len(users)]
    ipt.append({"number": prev_tx_h, "output": {"value": value, "pubkey": user_keys[sender][1]}})
    print(ipt)
    opt.append({"value": value, "pubkey": user_keys[receiver][1]})
    sig = create_signature(ipt, opt, user_keys[sender][0])
    tx = Transaction(ipt=ipt, opt=opt, signature=sig)
    prev_tx_h = tx.number
    tx_pool.append(tx)
    tx.print()


# 3 invalid tx
# invalid sig
fake_tx_number = H('I exist'.encode('utf-8')).hexdigest()
ipt = [{"number": fake_tx_number, "output": {"value": value, "pubkey": user_keys["PF"][1]}}]
opt = [{"value": value, "pubkey": user_keys["KC"][1]}]
wrong_key = SigningKey.generate()
sig = create_signature(ipt, opt, wrong_key)
invalid_tx_1 = Transaction(ipt=ipt, opt=opt, signature=sig)
invalid_tx_1.print()
print(invalid_tx_1.input, invalid_tx_1.output)

# sum of input values does not match with sum of output values
invalid_tx_tmp_1 = tx_pool[4]
i = invalid_tx_tmp_1.input
o = [{"value": 30, "pubkey": user_keys["PIL"][1]}, {"value": 15, "pubkey": i[0]["output"]["pubkey"]}]
sig = create_signature(i, o, user_keys['O'][0])
invalid_tx_2 = Transaction(ipt=i, opt=o, signature=sig)
invalid_tx_2.print()
print(invalid_tx_2.input, invalid_tx_2.output)

# double spend
invalid_tx_tmp_2 = tx_pool[5]
i = invalid_tx_tmp_2.input
o = [{"value": value, "pubkey": user_keys["PF"][1]}]
sig = create_signature(i, o, user_keys['KC'][0])
invalid_tx_3 = Transaction(ipt=i, opt=o, signature=sig)
invalid_tx_3.print()
print("Double Spending")
print(invalid_tx_3.input, invalid_tx_3.output)


# add invalid tx to tx list
tx_pool.insert(4, invalid_tx_1)
tx_pool.insert(7, invalid_tx_2)
tx_pool.insert(12, invalid_tx_3)

tx_list = []
for i in tx_pool:
    tx_tmp = {}
    tx_tmp["number"] = i.number
    tx_tmp["input"] = i.input
    tx_tmp["output"] = i.output
    tx_tmp["sig"] = str(i.sig)
    tx_list.append(tx_tmp)


# save all the transactions locally
with open('txs', 'w') as file:
    file.write(json.dumps(tx_list, indent=4))

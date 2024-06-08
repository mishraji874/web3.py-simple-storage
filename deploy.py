from solcx import compile_standard, install_solc
import json
from web3 import Web3
from dotenv import load_dotenv
import os

load_dotenv()

install_solc("0.6.0")

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()
    print(simple_storage_file)
    
#Compile our solidity

compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]
                }
            }
        },
    },
    solc_version= "0.6.0",
)

print(compiled_sol)


with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file) #used to convert python object to json
    


#get bytecode
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"]["bytecode"]["object"]
print(bytecode)


#get abi
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]
print(abi)



#for connecting to ganache
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
chain_id = 1337
my_address = "0x025896caB5199De7A286f6b16Baa54061F63fB4D"
# private_key = "0x9e97eddad1c091cd8df2a9cb2b92c6743c94f8092c894a9c763f4be1da1d186a"
private_key = os.getenv("PRIVATE_KEY")
print(private_key)


#create the contract in python
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)

#get latest transactions
nonce = w3.eth.get_transaction_count(my_address)
print(nonce)



#1. Build a transaction
#2. Sign a transaction
#3. Send a transaction

#build
transaction = SimpleStorage.constructor().build_transaction({"chainId":chain_id, "from": my_address, "nonce": nonce})
print(transaction)

#sign
signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
print(signed_txn)

print("Deploying contract...")
#send
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

print("Deployed")

#working with the contract, you always need
#contract abi
#contract address
simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)

#call -> simulate making the call and getting a return value
#transact -> actually make a state change

#initial value of the favorite number
print(simple_storage.functions.retrieve().call())
print(simple_storage.functions.store(15).call())

print("Updating contract...")

store_transaction = simple_storage.functions.store(15).build_transaction({
    "chainId": chain_id, "from": my_address, "nonce": nonce + 1
})
signed_store_txn = w3.eth.account.sign_transaction(store_transaction, private_key=private_key)
send_store_tx = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(send_store_tx)

print("Updated")
print(simple_storage.functions.retrieve().call())
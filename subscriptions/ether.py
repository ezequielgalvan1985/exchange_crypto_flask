import pika
import httpx
from web3 import Web3, EthereumTesterProvider

#1 conectarse a la red de ethereum
#
ether_wss = "wss://eth-sepolia.g.alchemy.com/v2/0h5Sn2tIlX9I6df5wejlR3NqotbLfYw3"
w3 = Web3(Web3.WebsocketProvider(ether_wss))
WETH_ADDRESS = '0x0B305C4AD6B1A1Fe6dCBAE8BEEE931878c6B2Ef3'

block = w3.eth.get_block('latest')
for tx_hash in block.transactions:
    tx = w3.eth.get_transaction(tx_hash)
    if tx['to'] == WETH_ADDRESS:
        print(f'Found interaction with WETH contract! {tx}')
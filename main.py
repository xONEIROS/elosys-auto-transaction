from web3 import Web3
import logging
from colorama import init, Fore, Style
import pyfiglet
import os
import time
import random
import json

def print_banner(text):
    try:
        fonts = ["slant", "banner3-D", "block", "bubble", "digital", "standard"]
        font = random.choice(fonts)
        ascii_banner = pyfiglet.figlet_format(text, font=font)
        print(ascii_banner)
    except Exception as e:
        print(Fore.RED + f"Error displaying banner: {e}")

init()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)


config = {
    "rpc_url": "https://testnet-rpc.elosys.io",
    "gas_price_gwei": 20,
    "gas_limit": 21000,
    "chain_id": 51215,
    "coin_symbol": "tELO"
}

rpc_url = config['rpc_url']
web3 = Web3(Web3.HTTPProvider(rpc_url))

if not web3.is_connected():
    logger.error(Fore.RED + "Failed to connect to RPC URL")
    exit()

gas_price = web3.to_wei(config['gas_price_gwei'], 'gwei')
gas_limit = config['gas_limit']

def generate_wallets(num_wallets, filename='wallets.json'):
    wallets = []
    for _ in range(num_wallets):
        account = web3.eth.account.create()
        wallets.append({'address': account.address, 'private_key': account._private_key.hex()})
    
    with open(filename, 'w') as file:
        json.dump(wallets, file, indent=4)
    
    logger.info(Fore.GREEN + f"Generated {num_wallets} wallets and saved to {filename}.")
    return wallets

def load_wallets(filename='wallets.json'):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            wallets = json.load(file)
    else:
        logger.error(Fore.RED + f"File {filename} not found.")
        exit()
    return wallets

def send_eth(to_address, amount_eth, private_key, gas_price):
    try:
        account = web3.eth.account.from_key(private_key)
        my_address = account.address
        nonce = web3.eth.get_transaction_count(my_address)

        transaction = {
            'nonce': nonce,
            'to': to_address,
            'value': web3.to_wei(amount_eth, 'ether'),
            'gas': gas_limit,
            'gasPrice': gas_price,
            'chainId': config['chain_id']
        }

        signed_transaction = web3.eth.account.sign_transaction(transaction, private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_transaction.raw_transaction)
        return tx_hash.hex()
    except Exception as e:
        logger.error(Fore.RED + f"Failed to send {config['coin_symbol']} to {to_address}: {str(e)}")
        if 'replacement transaction underpriced' in str(e):
            logger.info(Fore.YELLOW + "Increasing gas price and retrying...")
            new_gas_price = gas_price + web3.to_wei(1, 'gwei')  
            return send_eth(to_address, amount_eth, private_key, new_gas_price)
        raise 

def print_separator(color):
    print(color + "-"*60)

def main():
    print_banner("0xOneiros")
    
    private_key = input(Style.BRIGHT + Fore.CYAN + "Please enter your private key: ")
    
    num_wallets = int(input(Style.BRIGHT + Fore.CYAN + "Enter the number of wallets to generate: "))
    wallets = generate_wallets(num_wallets)
    
    for wallet in wallets:
        recipient_address = wallet['address']
        print_separator(Fore.BLUE)
        
        try:
            amount_eth = round(random.uniform(0.00001, 0.005), 8)
            tx_hash = send_eth(recipient_address, amount_eth, private_key, gas_price)
            tx_url = f"https://testnet-explorer.elosys.io/tx/{tx_hash}"
            logger.info(Fore.YELLOW + f"Successfully sent {amount_eth} {config['coin_symbol']} to {recipient_address}. {tx_url}")
            print(Fore.YELLOW + f"Successfully sent {amount_eth} {config['coin_symbol']} to {recipient_address}. {tx_url}")
            print_separator(Fore.BLUE)
            delay = random.randint(5, 11)  
            time.sleep(delay)
        except Exception as e:
            print(Fore.RED + f"Failed to send {config['coin_symbol']} to {recipient_address}.")
            logger.error(Fore.RED + f"Failed to send {config['coin_symbol']} to {recipient_address}: {str(e)}")
            print_separator(Fore.BLUE)

if __name__ == "__main__":
    main()

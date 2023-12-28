from starknet_py.net.account.account import Account
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models import StarknetChainId
from starknet_py.contract import Contract
import json
import asyncio
import time


ADDRESS = '<YOUR STARKNET ADDRESS HERE>'
PRIVATE_KEY = '<YOUR STARKNET PRIVATE KEY HERE>'

# Amount of $LEA to sell
AMOUNT_TO_SELL = 1000.5


stark_client = FullNodeClient('https://starknet-mainnet.public.blastapi.io', net='mainnet')
account = Account(address=ADDRESS, client=stark_client,
                  key_pair=KeyPair.from_private_key(int(PRIVATE_KEY[2:], 16)),
                  chain=StarknetChainId.MAINNET)


jedi_address = 0x41fd22b238fa21cfcf5dd45a8548974d8263b3a531a60388411c5e230f97023
ethTokenAddress = 0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7
memeTokenAddress = 0x0412396984a874866f68334f0997b0b897e3a0b29a4f8d64861126b9bd171a98
pool_address = 0x398082cc60d530ed0d2b7e9c09239918f4561133b895c247cc6c1229ab904f8

dex_contract = Contract(jedi_address, json.load(open('abi/jediswap.json', 'r')), account)
meme_token_contract = Contract(memeTokenAddress, json.load(open('abi/token.json', 'r')), account)

amount_to_sell_int = int(AMOUNT_TO_SELL * 10 ** 18)
transfer_amount = amount_to_sell_int // 50
swap_amount = amount_to_sell_int - transfer_amount


async def main():
    transfer_call = meme_token_contract.functions['transfer'].prepare(pool_address, transfer_amount)
    approve_call = meme_token_contract.functions['approve'].prepare(jedi_address, swap_amount)
    swap_args = (swap_amount, 0, (memeTokenAddress, ethTokenAddress), account.address, int(time.time()) + 600)
    swap_call = dex_contract.functions['swap_exact_tokens_for_tokens'].prepare(*swap_args)
    calls = [
        transfer_call,
        approve_call,
        swap_call,
    ]
    tx = await account.execute(calls=calls, auto_estimate=True)
    print('Swap tx hash:', hex(tx.transaction_hash))
    print('Tx will be visible in the scanner after a while')


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())

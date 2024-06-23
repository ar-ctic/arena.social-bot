from web3 import Web3
from web3.middleware import geth_poa_middleware
import asyncio
import json
import logging
import time
import requests
import threading
import config
import db


"""
sell amount shares with web3py
"""
def sellShare(keySubject, amount) -> None:
    print(amount)
    try:
        # Build Transaction
        # https://web3py.readthedocs.io/en/v5/contracts.html?highlight=build_transaction#web3.contract.ContractFunction.build_transaction
        unsigned_sell_transaction = contract.functions.sellShares(keySubject, amount).build_transaction({
            "from": acct.address,
            "nonce": web3.eth.get_transaction_count(acct.address),

        })

        # Sign transaction
        # https://web3py.readthedocs.io/en/v5/contracts.html?highlight=sign_transaction#web3.contract.ContractFunction.build_transaction
        signed_sell_transaction = web3.eth.account.sign_transaction(unsigned_sell_transaction, private_key = acct.key)

        # Send Transaction
        # https://web3py.readthedocs.io/en/v5/web3.eth.html#web3.eth.Eth.send_raw_transaction
        tx_hash = web3.eth.send_raw_transaction(signed_sell_transaction.rawTransaction)
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

        tx_hash = Web3.to_json(tx_hash)

        if receipt['status'] == 0:
            print(f"\nTransaction failed: {tx_hash}")
            return

        print(f"\nTransaction successfull: {tx_hash}")

        db.rem_key(keySubject)

    except Exception as error:
        error = str(error)
        print(f"\nsellShare error: {error}")
        
        if error == 'execution reverted: Insufficient shares':
            print("INSUFFICIENT SHARES")
            db.rem_key(keySubject)

        # You are the last keyholder. Can´t sell last key
        elif error == 'Panic error 0x11: Arithmetic operation results in underflow or overflow.':
            print("Arithmetic operation results in underflow or overflow.")
            db.rem_key(keySubject)



"""
Logic to check when/if key should be sold
"""
def check_if_sell(data, deltaTime) -> None: 
    if data['amount'] == 1 and deltaTime > 7200:
        print(f'Sell shares {data["keySubject"]}, only 1 share + deltaTime > 7200')
        sellShare(data["keySubject"], data["amount"])

    elif data['amount'] == 1 and relative_profit > 90:
        print(f'Sell shares {data["keySubject"]}, only 1 share + profit > 90%')
        sellShare(data["keySubject"], data["amount"])


    elif data['amount'] == 2 and deltaTime > 14400:
        print(f'Sell shares {data["keySubject"]}, only 2 share + deltaTime > 14400')
        sellShare(data["keySubject"], data["amount"])

    elif data['amount'] == 2 and relative_profit > 90:
        print(f'Sell shares {data["keySubject"]}, only 2 share + profit > 90%')
        sellShare(data["keySubject"], data["amount"])


    elif data['amount'] == 3 and deltaTime > 18000:
        print(f'Sell shares {data["keySubject"]}, 3 share + deltaTime > 18000')
        sellShare(data["keySubject"], data["amount"])

    elif data['amount'] == 3 and relative_profit > 400:
        print(f'Sell shares {data["keySubject"]}, 3 share + profit > 400%')
        sellShare(data["keySubject"], data["amount"])


    elif data['amount'] == 5 and deltaTime > 21600:
        print(f'Sell shares {data["keySubject"]}, 5 share + deltaTime > 21600')
        sellShare(data["keySubject"], data["amount"])

    elif data['amount'] == 5 and relative_profit > 400:
        print(f'Sell shares {data["keySubject"]}, 5 share + profit > 400%')
        sellShare(data["keySubject"], data["amount"])


    elif data['amount'] == 9 and deltaTime > 40000:
        print(f'Sell shares {data["keySubject"]}, 9 share + deltaTime > 40000')
        sellShare(data["keySubject"], data["amount"])

    elif data['amount'] == 9 and relative_profit > 400:
        print(f'Sell shares {data["keySubject"]}, 9 share + profit > 400%')
        sellShare(data["keySubject"], data["amount"])

    elif data['amount'] == 12 and deltaTime > 60000:
        print(f'Sell shares {data["keySubject"]}, 12 share + deltaTime > 60000')
        sellShare(data["keySubject"], data["amount"])

    elif data['amount'] == 12 and relative_profit > 600:
        print(f'Sell shares {data["keySubject"]}, 12 share + profit > 600%')
        sellShare(data["keySubject"], data["amount"])

    elif data['amount'] == 15 and deltaTime > 80000:
        print(f'Sell shares {data["keySubject"]}, 12 share + deltaTime > 80000')
        sellShare(data["keySubject"], data["amount"])

    elif data['amount'] == 15 and relative_profit > 1000:
        print(f'Sell shares {data["keySubject"]}, 12 share + profit > 1000%')
        sellShare(data["keySubject"], data["amount"])



"""
iterate through database
"""

def check_database() -> None:
    keys = db.get_database()
    nowTime = time.time()
    
    # Used to calc current key holdings
    sumSellPrice_wei = 0
    ethBalance_wei = web3.eth.get_balance(config.my_wallet)
    ethBalance = Web3.from_wei(ethBalance_wei, 'ether')

    for key in keys:

        data = {
            "keySubject": key[0],
            "amount": key[1],
            "buyPrice": key[2],
            "sellPrice": key[3],
            "relativeProfit": key[4],
            "totalSupply": key[5],
            "timeStamp": key[6],

        }
        try:

            totalSupply = 0

            sellPrice = contract.functions.getSellPriceAfterFee(data["keySubject"], data["amount"]).call()
            sumSellPrice_wei += sellPrice


            relative_profit = (sellPrice-data["buyPrice"])/data["buyPrice"] * 100

            # update db if new data
            if data["sellPrice"] != sellPrice or data["relativeProfit"] != relative_profit or data["relativeProfit"] != totalSupply:

                db.update_sellPrice_relativeProfit(data["keySubject"], sellPrice, relative_profit, totalSupply)


            # time since buy
            deltaTime = nowTime - data["timeStamp"]
            
            check_if_sell(data, deltaTime)


        except Exception as error:
            print(f'\ncheck_database error for subject {data["keySubject"]}: {error}')
        #db.addError(data["keySubject"], data["amount"])
        #db.rem_key(data["keySubject"])

    db.show_db()
    sumSellPrice = Web3.from_wei(sumSellPrice_wei, 'ether')
    totalBalance = ethBalance + sumSellPrice
    print(f"\nAVAX in keys: {sumSellPrice}\nAVAX balance: {ethBalance}\nAVAX total: {totalBalance}")



def gas_logic(amount):
    if amount == 1:
        #print(f"SET GAS BACK TO 46 GWEI")
        gas = web3.to_wei('46', 'gwei')
    elif amount == 2:
        #print(f"SET GAS TO 75 GWEI")
        gas = web3.to_wei('75', 'gwei')

    elif amount == 3:
        #print(f"SET GAS TO 100 GWEI GAS")
        gas = web3.to_wei('100', 'gwei')

    elif amount == 5:
        gas = web3.to_wei('700', 'gwei')

    elif amount == 9:
        #print("SET GAS TO 1300 GWEI")
        gas = web3.to_wei('1300', 'gwei')

    elif amount == 12:
        #print("SET GAS TO 1500 GWEI")
        gas = web3.to_wei('1500', 'gwei')

    elif amount == 15:
        #print("SET GAS TO 1800 GWEI")
        gas = web3.to_wei('1800', 'gwei')
        
    return gas


"""
buy amount shares with web3py
"""
def buyShare(sharesSubject, amount, value) -> None:
    
    
    gas = gas_logic(amount)

    try:
        # Build Transaction 
        # https://web3py.readthedocs.io/en/v5/contracts.html?highlight=build_transaction#web3.contract.ContractFunction.build_transaction
        unsigned_buy_transaction = contract.functions.buyShares(sharesSubject, amount).build_transaction({
            "from": acct.address,
            "nonce": web3.eth.get_transaction_count(acct.address),
            "value": value,
            "gasPrice": gas,
            

        })

        # Sign transaction 
        # https://web3py.readthedocs.io/en/v5/contracts.html?highlight=sign_transaction#web3.contract.ContractFunction.build_transaction
        signed_buy_transaction = web3.eth.account.sign_transaction(unsigned_buy_transaction, private_key = acct.key)

        # Send Transaction
        # https://web3py.readthedocs.io/en/v5/web3.eth.html#web3.eth.Eth.send_raw_transaction
        tx_hash = web3.eth.send_raw_transaction(signed_buy_transaction.rawTransaction)

 
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        tx_hash = Web3.to_json(tx_hash)
        print(f"\nTrying to buy Amount: {amount}, Address '{sharesSubject}' for: {Web3.from_wei(value, 'ether')} AVAX")

        if receipt['status'] == 0:
            print(f"\nTransaction failed: {tx_hash}\n")
            getPrice = contract.functions.getBuyPriceAfterFee(sharesSubject, amount).call()
            print(f"Actual price: {Web3.from_wei(getPrice, 'ether')} AVAX")
            
            return
        
        print(f"\nTransaction successfull: {tx_hash}\n")
        
        db.addKey(sharesSubject, amount, value, '0', '0', time.time())

        """
        If more than 9 keys are bought check db immediatly as 
        the account has more than > 50_000 follower -> probable price spike at listing
        """ 
        if amount >= 9:
            check_database()

    except Exception as error:
        print(f"\nbuyShare error: {sharesSubject}, {error}")
        getPrice = contract.functions.getBuyPriceAfterFee(sharesSubject, amount).call()
        print(f"Actual price: {Web3.from_wei(getPrice, 'ether')} AVAX")



"""
logic to buy x amount of keys if user has y amount of follower on twitter
"""
def buy_amount_logic(address, twitterFollowers) -> None:

    if 250 <= twitterFollowers <= 500:
        buyShare(address, config.buyAmount_1, config.buyValue_1)
        
    elif 500 <= twitterFollowers <= 2500:
        buyShare(address, config.buyAmount_2, config.buyValue_2)
        
    elif 2500 <= twitterFollowers <= 7500:
        buyShare(address, config.buyAmount_3, config.buyValue_3)
        
    elif 7500 <= twitterFollowers <= 15000:
        buyShare(address, config.buyAmount_5, config.buyValue_5)
        
    elif 15000 <= twitterFollowers <= 50000:
        buyShare(address, config.buyAmount_9, config.buyValue_9)
        
    elif 50000 <= twitterFollowers <= 150000:
        buyShare(address, config.buyAmount_12, config.buyValue_12)
        
    elif twitterFollowers > 150000:
        buyShare(address, config.buyAmount_15, config.buyValue_15)
        
    return


"""
keeps looking for newest registration using their api
cnt is used to check the database every x requests
"""
def main():
    print("\n####### MAIN START #######\n")
    
    url = 'https://api.starsarena.com/user/page'
    
    oldSubject = ''
    cnt = 0
    while True:
        try:
            
            r = requests.get(url, headers = headers, timeout = 2)
           
            data = r.json()['users'][0]
            
            cnt+=1

            """
            compare newest registration to our last, if the same request again after sleep
            """
            if data['twitterHandle'] == oldSubject:
                time.sleep(0.25)
                continue

            oldSubject = data['twitterHandle']
            keyValue = data['keyPrice']
            
            """
            '6600000000000000' = key price if the owner is the only shareholder and only holds one key
            guard to not buy into owner frontrunning his own keys
            """
            if keyValue == '6600000000000000':

                address = web3.to_checksum_address(data['address'])
                twitterFollowers = int(data['twitterFollowers'])

                buy_amount_logic(address, twitterFollowers)

            

            time.sleep(0.5)

            if cnt > 150:
                cnt = 0
                print("CHECK DB")
                
                check_db = threading.Thread(target = check_database, args = [])
                check_db.start()


        except Exception as error:
            print('main', error)
            time.sleep(0.5)


if __name__ == '__main__':

    wss = config.wss
    web3 = Web3(Web3.WebsocketProvider(wss))
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)
    print(f"\nConnected to Blockchain: {web3.is_connected()}\n")

    # get smart contract
    router = web3.to_checksum_address(config.to_address)
    contract = web3.eth.contract(address = router, abi = config.starshares_abi)


    start_balance_wei = web3.eth.get_balance(config.my_wallet)
    start_balance = Web3.from_wei(start_balance_wei, 'ether')

    acct = web3.eth.account.from_key(config.pk)
    
    headers = {'User-Agent': 'Mozilla/5.0','authorization': config.browser_auth}

    check_db = threading.Thread(target = check_database, args = [])
    check_db.start()
    
    
    main()
import logging
import requests
import json
import concurrent.futures

from common.constants import region, items, keywords

logging.basicConfig(level=logging.INFO)

class Contract:
    def __init__(self, contract_id, price, title):
        self.contract_id = contract_id
        self.price = price
        self.title = title

def pull_blobs() -> list:
    """Pulls all contracts in specified region and combines them into a mega \
        blob"""
    blob = []
    for p in range(1, 10):
        resp = requests.get(f'https://esi.evetech.net/latest/contracts/public/{region}/?datasource=tranquility&page={p}')
        logging.info(f'code: {resp.status_code} on page {p}')
        if resp.status_code == 200:
            blob = [*blob, *resp.json()]
        else:
            logging.info('Hit end or some error')
            break
    return blob

def title_search(blob: list) -> list:
    """searches all the contracts for keywords in the title, returns list of \
        contract hits"""
    contracts = []
    logging.info('searching...')
    for k in keywords:
        for c in blob:
            if c['title'].lower().__contains__(k):
                if any(obj.contract_id == c['contract_id'] for obj in contracts):
                    pass
                else:
                    print(c['contract_id'], c['title'])
                    contracts.append(Contract(c['contract_id'], c['price'], c['title']))
    return contracts

def item_search(contracts: list):
    """searches a list of contracts for an item #"""
    print("*********************************************")
    for c in contracts:
        resp = requests.get(f'https://esi.evetech.net/latest/contracts/public/items/{c.contract_id}/?datasource=tranquility')
        for r in resp.json():
            print(r['type_id'])
            try:
                if r['type_id'] in items:
                    if 'is_blueprint_copy' in r:
                        if r['is_blueprint_copy'] == 'true':
                            print(f'contract {c.contract_id} matches! Price is {c.price:,}')
                        else:
                            pass
                    else:
                        print(f'contract {c.contract_id} matches! Price is {c.price:,}')
            except Exception as err:
                logging.error(err)


if __name__ == '__main__':
    blob = pull_blobs()
    contracts = title_search(blob)

    pool = concurrent.futures.ThreadPoolExecutor(max_workers=20)
    
    step = 50
    for i in range(0, len(contracts), step):
        print('thread spawn')
        x = i
        pool.submit(item_search(contracts[x:x+step]))

    pool.shutdown(wait=True)

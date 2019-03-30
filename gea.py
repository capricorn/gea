import time
import json
import threading
from collections import OrderedDict

import requests

def get_last_csv_entry(csv_data):
    csv_data = csv_data.split('\n')
    csv_data.pop()  # Remove empty '' at end of list from split

    return csv_data[-1].split(', ')

def get_items_from_csv():
    with open('items.csv', 'r') as csv:
        data = csv.read()
        return (list(map(lambda k: int(k[:-1]), data.splitlines())))

def read_proxy_creds():
    with open('proxy.txt', 'r') as f:
        return f.read()[:-1]

def append_item_data(item):
    proxy = { 'http': read_proxy_creds() }
    r = requests.get('http://services.runescape.com/m=itemdb_oldschool/api/graph/' + str(item) + '.json', proxies=proxy)
    data = json.loads(r.text, object_pairs_hook=OrderedDict)
    with open('./csv/' + str(item) + '.csv', 'a+') as f:
        f.seek(0)
        csv_data = f.read()

        last_entry_ts = 0
        if csv_data != '':
            last_entry_ts = int(get_last_csv_entry(csv_data)[0])

        for d in data['daily']:
            if int(d) > last_entry_ts:
                f.write('{}, {}\n'.format(d, data['daily'][d]))

items = get_items_from_csv()
groups = [ items[i:(i+5) % len(items)] for i in range(0, len(items), 5) ] 

def main():
    for items in groups:
        threads = []
        for item in items:
            thread = threading.Thread(target=append_item_data, args=(item,))
            threads.append(thread)

        [ thread.start() for thread in threads ]
        [ thread.join() for thread in threads ]
        print('Recorded group ' + str(items))
        time.sleep(1)

if __name__ == '__main__':
    main()

import time
import json
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

def record_update_ts(ts):
    with open('ts.txt', 'a+') as f:
        f.seek(0)
        stamps = list(map(lambda k: int(k), f.read().splitlines()))
        if stamps == [] or ts > (stamps[-1:][0] + 30):
            f.write('%d\n' % (ts))

def append_item_data(item):
    r = requests.get('http://services.runescape.com/m=itemdb_oldschool/api/graph/' + str(item) + '.json')
    data = json.loads(r.text, object_pairs_hook=OrderedDict)
    with open(str(item) + '.csv', 'a+') as f:
        f.seek(0)
        csv_data = f.read()

        last_entry_ts = 0
        if csv_data != '':
            last_entry_ts = int(get_last_csv_entry(csv_data)[0])

        for d in data['daily']:
            if int(d) > last_entry_ts:
                record_update_ts(int(time.time()))  # How wrong is the ts associated with the data?
                print('{}: Writing {}'.format(time.time(), d))
                f.write('{}, {}\n'.format(d, data['daily'][d]))

items = get_items_from_csv()
try:
    while True:
        for item in items:
            print('Attempting item update: {}'.format(item)) 
            append_item_data(item)
            time.sleep(2)
except KeyboardInterrupt:
    pass

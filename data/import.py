#!/usr/bin/env python

import sys, csv, sqlite3, re

num = re.compile('^[0-9,]*$')
commas = re.compile(r'[^0-9]')

reader = csv.reader(open(sys.argv[1]))

conn = sqlite3.connect('iedata.sqlite3')

first_row = reader.next()
conn.execute('drop table if exists orig_data')
conn.execute('create table orig_data (' + ", ".join([name.lower() for name in first_row]) + ')')

query = 'insert into orig_data values(' + ','.join(['?'] * len(first_row)) + ')'
for row in reader:
    row = map(lambda field: commas.sub('', field) if num.match(field) else field, row)
    conn.execute(query, row)

conn.commit()
conn.execute('create index if not exists spe_id_index on orig_data (spe_id)')
conn.execute('create index if not exists can_id_index on orig_data (can_id)')
conn.commit()
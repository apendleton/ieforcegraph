#!/usr/bin/env python

import sqlite3

conn = sqlite3.connect('iedata.sqlite3')
c = conn.cursor()

conn.execute('drop table if exists can_org_weights')
conn.execute('create table can_org_weights (id integer primary key autoincrement not null, organization_id integer, candidate_id integer, weight float)')
r = c.execute('select id, ext_id, total_for, total_against, name from candidates')
candidates = r.fetchall()
r = c.execute('select id, ext_id, total, name from organizations')
organizations = r.fetchall()
for organization in organizations:
    print organization[3]
    for candidate in candidates:
        weight = 1
        dollars_result = c.execute("select sup_opp, sum(exp_amo) from orig_data where can_id = ? and spe_id = ? group by sup_opp", (candidate[1], organization[1])).fetchall()
        dollars = dict(dollars_result)
        if 'S' in dollars and candidate[2]:
            weight -= (dollars['S'] / candidate[2])
        if 'O' in dollars and candidate[3]:
            weight += (dollars['O'] / candidate[3])
        c.execute('insert into can_org_weights (organization_id, candidate_id, weight) values (?, ?, ?)', (organization[0], candidate[0], weight))
conn.commit()
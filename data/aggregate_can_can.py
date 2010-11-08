#!/usr/bin/env python

import sqlite3

conn = sqlite3.connect('iedata.sqlite3')
c = conn.cursor()

conn.execute('drop table if exists can_can_weights')
conn.execute('create table can_can_weights (id integer primary key autoincrement not null, candidate1_id integer, candidate2_id integer, weight float)')
r = c.execute('select id, ext_id, total, name from candidates')
candidates = r.fetchall()
for thisOne in candidates:
    print thisOne[3]
    for otherOne in filter(lambda s: int(s[0]) < int(thisOne[0]), candidates):
        # scary death query: finds the number of dollars for each candidate that came from groups that also spent money on the other candidate
        dollars_result = c.execute(
            "select can_id, sum(exp_amo) from orig_data where spe_id in " +
            "(select distinct organizations.ext_id from orig_data as o1, orig_data as o2, organizations " +
            "where o1.spe_id = organizations.ext_id and o2.spe_id = organizations.ext_id and o1.can_id = ? and o2.can_id = ? " +
            "and upper(o1.sup_opp) = 'S' and upper(o2.sup_opp) = 'S')" +
            "and upper(sup_opp) = 'S' and can_id in (?, ?) group by can_id",
            (thisOne[1], otherOne[1], thisOne[1], otherOne[1])
        )
        dollars = dict(dollars_result.fetchall())
        if dollars:
            thisWeight = dollars[thisOne[1]] / float(thisOne[2]) if thisOne[2] else 0
            otherWeight = dollars[otherOne[1]] / float(otherOne[2]) if otherOne[2] else 0
            weight = (thisWeight + otherWeight) / 2
        else:
            weight = 0
        weight = 1 - weight
        c.execute('insert into can_can_weights (candidate1_id, candidate2_id, weight) values (?, ?, ?)', (thisOne[0], otherOne[0], weight))
    c.execute('insert into can_can_weights (candidate1_id, candidate2_id, weight) values (?, ?, ?)', (thisOne[0], thisOne[0], 0))
conn.commit()
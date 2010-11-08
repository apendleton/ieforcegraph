#!/usr/bin/env python

import helpers, sqlite3, re
from django.utils.datastructures import SortedDict

conn = sqlite3.connect('iedata.sqlite3')
c = conn.cursor()

commas = re.compile(r'[^0-9]')

# candidates
conn.execute('drop table if exists candidates')
conn.execute('create table candidates (id integer primary key autoincrement not null, name text, ext_id text, party char(1), state text, district text, seat text, total float)')
r = c.execute('select distinct can_id from orig_data where can_id != \'\'')
for row in r.fetchall():
    id = row[0]
    matches = c.execute('select * from orig_data where can_id = ?', (id,)).fetchall()
    
    can = SortedDict()
    
    # get the longest name and standardize it
    can['name'] = helpers.standardize_politician_name(sorted(matches, cmp=lambda a, b: cmp(len(a[1]), len(b[1])), reverse=True)[0][1])
    
    # candidate ID
    can['ext_id'] = id
    
    # candidate party: get the longest, again, and check for Democrat or Republican in it
    party = sorted(matches, cmp=lambda a, b: cmp(len(a[8]), len(b[8])))[0][8].lower()
    if 'democrat' in party:
        can['party'] = 'D'
    elif 'republican' in party:
        can['party'] = 'R'
    else:
        can['party'] = 'I'
    
    # state: find the first non-blank one and use that if there is one, otherwise blank
    states = filter(lambda row: row[5], matches)
    if len(states) > 0:
        can['state'] = states[0][5]
    else:
        can['state'] = ''
    
    # district: same as state
    districts = filter(lambda row: row[6], matches)
    if len(districts) > 0:
        can['district'] = districts[0][6]
    else:
        can['district'] = ''
    
    # seat: should always be there and always be the same; use any one
    can['seat'] = matches[0][7]
    
    # total: get all of the pro-candidate dollars and sum them
    can['total'] = sum(map(lambda s: int('0' + commas.sub('', s[9])), filter(lambda m: m[12] == 'S', matches)))
    
    conn.execute('insert into candidates (' + ','.join(can.keys()) + ') values (' + ','.join('?' * len(can.keys())) + ')', can.values())

c.execute('create unique index if not exists pk on candidates (id)')

# Now let's try to fix the remaining names
for row in c.execute('select distinct cand_nam from orig_data where can_id = \'\'').fetchall():
    name = helpers.standardize_politician_name(row[0]).split(" ")
    first = name[0]
    last = name[-1]
    
    matches = c.execute('select name, ext_id from candidates where name like "' + first + '%" and name like "%' + last + '" order by total desc').fetchall()
    
    if len(matches) > 0:
        print "Updating %s to %s..." % (row[0], matches[0][0])
        c.execute('update orig_data set can_id = ? where cand_nam = ?', (matches[0][1], row[0]))
        print "Updated %s records." % c.rowcount
# Recalculate totals
for row in c.execute('select id, ext_id from candidates').fetchall():
    c.execute('update candidates set total = (select sum(exp_amo) from orig_data where can_id = ?) where id = ?', (row[1], row[0]))
conn.commit()

# organizations
conn.execute('drop table if exists organizations')
conn.execute('create table organizations (id integer primary key autoincrement not null, name text, ext_id text, partisanship float, total float)')
r = c.execute('select distinct spe_id from orig_data where spe_id != \'\'')
for row in r.fetchall():
    id = row[0]
    matches = c.execute('select * from orig_data where spe_id = ?', (id,)).fetchall()
    
    org = SortedDict()
    
    # get the longest name and standardize it
    org['name'] = helpers.standardize_organization_name(sorted(matches, cmp=lambda a, b: cmp(len(a[3]), len(b[3])), reverse=True)[0][3])
    
    # org ID
    org['ext_id'] = id
    
    # partisanship: keep zero for now (calculate in aggregates pass)
    org['partisanship'] = 0
    
    # total: get all of the money spent by the org
    org['total'] = sum(map(lambda s: int('0' + commas.sub('', s[9])), matches))
    
    conn.execute('insert into organizations (' + ','.join(org.keys()) + ') values (' + ','.join('?' * len(org.keys())) + ')', org.values())

c.execute('create unique index if not exists pk on organizations (id)')
conn.commit()
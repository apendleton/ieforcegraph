# borrowed from Influence Explorer
import re, string, datetime

def standardize_politician_name(name):
    name = strip_party(name)
    name = convert_to_standard_order(name)

    return convert_case(name)

def standardize_organization_name(name):
    name = name.strip()
    name = convert_case(name)

    if re.match(r'(?i)^\w*PAC$', name):
        name = name.upper() # if there's only one word that ends in PAC, make the whole thing uppercase
    else:
        name = re.sub(r'(?i)\bpac\b', 'PAC', name) # otherwise just uppercase the PAC part

    return name

def separate_affixes(name):
    # this should match both honorifics (mr/mrs/ms) and jr/sr/II/III
    matches = re.search(r'^\s*(?P<name>.*)\b((?P<honorific>m[rs]s?.?)|(?P<suffix>([js]r|I{2,})))[.,]?\s*$', name, re.IGNORECASE)
    if matches:
        return matches.group('name', 'honorific', 'suffix')
    else:
        return name, None, None

def strip_party(name):
    return re.sub(r'\s*\(\w+\)\s*$', '', name)

def convert_case(name):
    name = name if is_mixed_case(name) else string.capwords(name)
    name = uppercase_roman_numeral_suffix(name)
    return uppercase_the_scots(name)

def uppercase_roman_numeral_suffix(name):
    matches = re.search(r'(?i)(?P<suffix>\b[ivx]+)$', name)
    if matches:
        suffix = matches.group('suffix')
        return re.sub(suffix, suffix.upper(), name)
    else:
        return name

def uppercase_the_scots(name):
    matches = re.search(r'(?i)\b(?P<mc>ma?c)(?P<first_letter>\w)', name)
    if matches:
        mc = matches.group('mc')
        first_letter = matches.group('first_letter')
        return re.sub(mc + first_letter, mc.title() + first_letter.upper(), name)
    else:
        return name

def is_mixed_case(name):
    return re.search(r'[A-Z][a-z]', name)

def convert_to_standard_order(name):
    if '&' in name:
        return convert_running_mates(name)
    else:
        return convert_name_to_first_last(name)

def convert_name_to_first_last(name):
    split = name.split(',')
    if len(split) == 1: return split[0]

    trimmed_split = [ x.strip() for x in split ]

    trimmed_split.reverse()
    return ' '.join(trimmed_split)

def convert_running_mates(name):
    mates = name.split('&')
    fixed_mates = []
    for name in mates:
        fixed_mates.append(convert_name_to_first_last(name))

    return ' & '.join(fixed_mates).strip()

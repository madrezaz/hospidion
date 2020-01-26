from typing import List

from core.sql import SelectQuery


def purify(rows: List, header: tuple, query: SelectQuery):
    res = []
    for row in rows:
        if query.conditions is None or query.conditions.apply(row, header):
            res += [row]

    if query.target == '*':
        return res
    elif query.target[:4] == 'sum(' and query.target[-1] == ')':
        col = query.target[4:-1]
        col_i = header.index(col)
        return [(sum([row[col_i] for row in res]),)]
    else:
        cols = "".join(query.target.split()).split(',')
        nres = []
        for row in res:
            nr = []
            for col in cols:
                nr += [row[header.index(col)]]
            nres += [tuple(nr)]
        return nres
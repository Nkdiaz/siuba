from siuba.sql.verbs import collect, show_query, mutate, LazyTbl
from siuba.dply.verbs import Pipeable
from siuba.tests.helpers import SqlBackend, data_frame
from siuba import _

import pandas as pd

import pytest

pg_backend = SqlBackend("postgresql")

@pytest.fixture(scope = "module")
def df_tiny():
    return pg_backend.load_df(data_frame(x = [1,2]))

@pytest.fixture(scope = "module")
def df_wide():
    return pg_backend.load_df(data_frame(x = [1,2], y = [3,4], z = [5, 6]))

def rename_source(sql_backend, query):
    query.replace(sql_backend.tbl.name, "SRC_TBL")


def test_show_query_basic(df_tiny):
    q = df_tiny >> mutate(a = _.x.mean()) >> show_query(return_query = False)

    assert replace_source(str(q)) == """\
SELECT SRC_TBL.x, avg(SRC_TBL.x) OVER () AS a 
FROM SRC_TBL"""

def test_show_query_basic_simplify(df_tiny):
    q = df_tiny >> mutate(a = _.x.mean()) >> show_query(return_query = False, simplify=True)

    assert replace_source(str(q)) == """\
SELECT x, avg(x) OVER () AS a 
FROM SRC_TBL"""

def test_show_query_complex_simplify(df_wide):
    q = df_wide >>  mutate(a = _.x.mean(), b = _.a.mean())
    res = q >> show_query(return_query = False, simplify=True)

    assert replace_source(str(res)) == """\
SELECT a, avg(a) OVER () AS b 
FROM (SELECT *, avg(x) OVER () AS a 
FROM SRC_TBL) AS anon_1"""


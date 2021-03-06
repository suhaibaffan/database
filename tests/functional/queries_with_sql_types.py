# Copyright 2020 Alex Dukhno
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import psycopg2 as pg
import pytest


@pytest.fixture(scope="session", autouse=True)
def create_cursor(request):
    try:
        conn = pg.connect(host="localhost", password="check_this_out", database="postgres")
        cur = conn.cursor()

        def close_all():
            conn.close()
            cur.close()

        request.addfinalizer(close_all)
    except Exception as e:
        assert False, str(e)
    return cur


def test_integer_types(create_cursor):
    cur = create_cursor
    try:
        cur.execute('create schema schema_name;')
        cur.execute('create table schema_name.table_name(si_col smallint, i_col integer, bi_col bigint);')

        cur.execute('insert into schema_name.table_name values (%d, %d, %d);' % (-32768, -2147483648, -9223372036854775808))
        cur.execute('insert into schema_name.table_name values (%d, %d, %d);' % (32767, 2147483647, 9223372036854775807))

        cur.execute('select * from schema_name.table_name;')
        r = cur.fetchmany(2)
        assert r == [(-32768, -2147483648, -9223372036854775808,), (32767, 2147483647, 9223372036854775807,)]
    finally:
        cur.execute('drop table schema_name.table_name;')
        cur.execute('drop schema schema_name;')


def test_character_types(create_cursor):
    cur = create_cursor
    try:
        cur.execute('create schema schema_name;')
        cur.execute(
            'create table schema_name.table_name(\
                col_no_len_chars char,\
                col_with_len_chars char(10),\
                col_var_char_smallest varchar(1),\
                col_var_char_large    varchar(20)\
                );')

        cur.execute(
            'insert into schema_name.table_name values (\'%s\', \'%s\', \'%s\', \'%s\');' % ('c', '1234567890', 'c', '12345678901234567890'))
        cur.execute(
            'insert into schema_name.table_name values (\'%s\', \'%s\', \'%s\', \'%s\');' % ('1', '1234567   ', 'c', '1234567890'))

        cur.execute('select * from schema_name.table_name;')
        r = cur.fetchmany(2)
        assert r == [('c', '1234567890', 'c', '12345678901234567890',), ('1', '1234567', 'c', '1234567890',)]
    finally:
        cur.execute('drop table schema_name.table_name;')
        cur.execute('drop schema schema_name;')

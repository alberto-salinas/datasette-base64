from datasette.app import Datasette
import pytest
import sqlite3

from datasette_base64 import prepare_connection

@pytest.fixture
def conn():
    conn = sqlite3.connect(":memory:")
    prepare_connection(conn)
    return conn


@pytest.mark.asyncio
async def test_plugin_is_installed():
    datasette = Datasette([], memory=True)
    response = await datasette.client.get("/-/plugins.json")
    assert 200 == response.status_code
    installed_plugins = {p["name"] for p in response.json()}
    assert "datasette-base64" in installed_plugins

@pytest.mark.parametrize("encoded,expected", (('QmxhZGUgUnVubmVy', 'Blade Runner'),('ICAgRHVuZSAgIA==', '   Dune   ')))
def test_decode(conn, encoded, expected):
    actual = conn.execute("select base64decode(?)", [encoded]).fetchall()[0][0]
    assert expected == actual

@pytest.mark.parametrize("decoded,expected", (('Blade Runner', 'QmxhZGUgUnVubmVy'),('   Dune   ', 'ICAgRHVuZSAgIA==')))
def test_encode(conn, decoded, expected):
    actual = conn.execute("select base64encode(?)", [decoded]).fetchall()[0][0]
    assert expected == actual
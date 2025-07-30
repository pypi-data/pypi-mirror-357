import emporiadb

def test_import_and_connect():
    # This test only checks import and instantiation, not actual API calls
    conn = emporiadb.connect(api_key="dummy_api_key")
    assert conn is not None 
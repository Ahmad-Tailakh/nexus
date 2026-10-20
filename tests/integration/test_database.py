def test_database_connection(session):
    assert session.is_active
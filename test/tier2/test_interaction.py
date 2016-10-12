def test_create_interaction(cdms_client):
    create_resp = cdms_client.create(
        'detica_interactionSet', {'Subject': 'Super bread factory'}
    )
    assert create_resp.ok

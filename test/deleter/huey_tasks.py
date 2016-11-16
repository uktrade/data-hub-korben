from korben.cdms_api.rest.api import CDMSRestApi
from huey_config import huey_instance



@huey_instance.task()
def delete_odata(odata_tablename, ident):
    cdms_client = CDMSRestApi()
    resp = cdms_client.delete(odata_tablename, "guid'{0}'".format(ident))
    print(resp)
    try:
        resp.json()  # TODO: handle deauth (could raise json.JSONDecodeError)
        return resp.status_code == 204
    except json.JSONDecodeError as exc:
        cdms_client.auth.setup_session(True)
    resp = cdms_client.delete(odata_tablename, "guid'{0}'".format(ident))
    print(resp)
    resp.json()
    return resp.status_code == 204

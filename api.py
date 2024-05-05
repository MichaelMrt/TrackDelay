import deutsche_bahn_api.api_authentication as dba
import config

api = dba.ApiAuthentication(config.CLIENT_ID, config.CLIENT_SECRET)
success: bool = api.test_credentials()
print(success)
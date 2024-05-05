import deutsche_bahn_api.api_authentication as dba

api = dba.ApiAuthentication("8f67e74b49f0ba8660339bb4cd826e98", "51a8654bf38ac547db6f60360673818d")
success: bool = api.test_credentials()
print(success)
from opengate_data import OpenGateClient
client = OpenGateClient()

south_client = OpenGateClient(False) #This works in K8 and uses internal K8 network


timeseries = client.new()\
    .with_identifier("identifier")\
    .with_format("dict")\
    .with_organization_name('organization_datalab')\
    .build()\
    .execute()

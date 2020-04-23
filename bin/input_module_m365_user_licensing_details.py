
# encoding = utf-8

import os
import sys
import time
import datetime
import json
import requests
import ta_azure_utils.utils as azutil
import ta_azure_utils.auth as azauth

def validate_input(helper, definition):
    pass

def collect_events(helper, ew):
    global_account = helper.get_arg("azure_app_account")
    client_id = helper.get_global_setting("client_id")
    client_secret = helper.get_global_setting("client_secret")
    tenant_id = helper.get_global_setting("tenant_id")
    collection_period = helper.get_arg("collection_period")
    source_type = helper.get_arg("data_sourcetype")

    
    access_token = azauth.get_graph_access_token(client_id, client_secret, tenant_id, helper)
    
    if(access_token):
        url = "https://graph.microsoft.com/beta/reports/getOffice365ActiveUserDetail(period='D%s')?$format=application/json" % collection_period

        try:
            subscriptions = azutil.get_items(helper, access_token, url)
        
            for subscription in subscriptions:
                event = helper.new_event(
                    data=json.dumps(subscription),
                    source=helper.get_input_type(), 
                    index=helper.get_output_index(),
                    sourcetype=source_type)
                ew.write_event(event)
        except Exception, e:
            raise e
    else:
        raise RuntimeError("Unable to obtain access token. Please check the Client ID, Client Secret, and Tenant ID")
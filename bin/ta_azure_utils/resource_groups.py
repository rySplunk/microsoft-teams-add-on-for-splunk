# encoding = utf-8
import sys
import json
import requests
from collections import defaultdict


def get_resource_groups(access_token, subscription_id):
    resource_groups = []
    url = "https://management.azure.com/subscriptions/%s/resourcegroups?api-version=2018-05-01" % (subscription_id)
    
    header = {'Authorization':'Bearer ' + access_token}

    try:
        r = requests.get(url,headers=header)
        r.raise_for_status()
        resource_group_data = json.loads(r.text)
    
        for resource_group in resource_group_data["value"]:
            resource_groups.append(resource_group)
    except Exception, e:
        raise e

    return resource_groups

def get_resource_groups_by_location(helper, access_token, subscription_id):
    groups = get_resource_groups(access_token, subscription_id)
    resource_groups_by_location = defaultdict(list)

    for group in groups:
        key = group["location"]
        resource_groups_by_location[key].append(group["name"])

    return resource_groups_by_location
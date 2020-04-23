# encoding = utf-8
import sys
import json
import datetime
import dateutil.parser
import urlparse
import requests

def get_items(helper, access_token, url, items=[]):

    headers = {}
    headers["Authorization"] = "Bearer %s" % access_token
    headers["Content-type"] = "application/json"
    proxies = get_proxy(helper, "requests")

    try:
        r = requests.get(url, headers=headers, proxies=proxies)

        # If we hit too many requests (status 429), return what has been collected so far.
        if r.status_code == 429:
            return items
        
        r.raise_for_status()
        response_json = None
        response_json = json.loads(r.content)
        items += response_json['value']

        if '@odata.nextLink' in response_json:
            nextLink = response_json['@odata.nextLink']

            # This should never happen, but just in case...
            if not is_https(nextLink):
                raise ValueError("nextLink scheme is not HTTPS. nextLink URL: %s" % nextLink)

            helper.log_debug("_Splunk_ nextLink URL (@odata.nextLink): %s" % nextLink)
            get_items(helper, access_token, nextLink, items)
        
    except Exception as e:
        raise e

    return items

def get_item(helper, access_token, url):
    headers = {}
    headers["Authorization"] = "Bearer %s" % access_token
    headers["Content-type"] = "application/json"
    proxies = get_proxy(helper, "requests")

    try:
        r = requests.get(url, headers=headers, proxies=proxies)
        r.raise_for_status()
        response_json = None
        response_json = json.loads(r.content)
        item = response_json
        
    except Exception as e:
        raise e

    return item



def test_by_url(helper, access_token, url):
    headers = {}
    headers["Authorization"] = "Bearer %s" % access_token
    headers["Content-type"] = "application/json"
    proxies = get_proxy(helper, "requests")

    try:
        r = requests.get(url, headers=headers, proxies=proxies)
        r.raise_for_status()
    except Exception as e:
        raise e

def get_start_date(helper, check_point_key, default_minutes):
    # Try to get a date from the check point first
    d = helper.get_check_point(check_point_key)
    
    # If there was a check point date, retun it.
    if (d not in [None,'']):
        return datetime.datetime(d['year'], d['month'], d['day'], d['hour'], d['minute'], d['second'], d['microsecond'])
    else:
        # No check point date, so look if a start date was specified as an argument
        d = helper.get_arg("start_date")
        if (d not in [None,'']):
            return dateutil.parser.parse(d)
        else:
            # If there was no start date specified, default to x minutes ago
            return (datetime.datetime.utcnow() - datetime.timedelta(minutes=default_minutes))

def get_end_date(helper, start_date, minutes):
    if not isinstance(start_date, datetime.datetime):
        start_date = dateutil.parser.parse(start_date)

    return start_date + datetime.timedelta(minutes=minutes)

def get_proxy(helper, proxy_type="requests"):
    proxies = None
    helper.log_debug("_Splunk_ Getting proxy server.")
    proxy = helper.get_proxy()
    
    if proxy:
        helper.log_debug("_Splunk_ Proxy is enabled: %s:%s" % (proxy["proxy_url"], proxy["proxy_port"]))
        if proxy_type.lower()=="requests":
            proxy_url = "%s:%s" % (proxy["proxy_url"], proxy["proxy_port"])
            proxies = {
                    "http" : proxy_url,
                    "https" : proxy_url
                }
        elif proxy_type.lower()=="event hub":
            proxies = {
                'proxy_hostname': proxy["proxy_url"],
                'proxy_port': int(proxy["proxy_port"]),
                'username': proxy["proxy_username"],
                'password': proxy["proxy_password"]
            }
            
    return proxies

def is_https(url):
    t = urlparse.urlparse(url)
    if t.scheme == "https":
        return True
    else:
        return False

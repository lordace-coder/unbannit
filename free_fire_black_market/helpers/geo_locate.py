from django.http import HttpRequest


def get_ip_from_request(request:HttpRequest):
    """
        Returns the ip of  a user from agiven request
    """
    req_headers = request.META
    x_forwarded_for_value = req_headers.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for_value:
        ip_addr = x_forwarded_for_value.split(',')[-1].strip()
    else:
        ip_addr = req_headers.get('REMOTE_ADDR')
    return ip_addr








    
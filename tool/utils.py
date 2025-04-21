from ipware import get_client_ip
import requests

def get_client_ip_address(request):
    ip, is_routable = get_client_ip(request)
    return ip if ip else "0.0.0.0"

def get_location_by_ip(ip):
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}")
        data = response.json()
        return {
            "city": data.get("city"),
            "country": data.get("country"),
            "lat": data.get("lat"),
            "lon": data.get("lon"),
        }
    except Exception as e:
        return {}
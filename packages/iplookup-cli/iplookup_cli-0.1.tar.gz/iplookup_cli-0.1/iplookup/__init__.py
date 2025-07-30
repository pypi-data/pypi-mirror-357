'''
IpLookup CLI

A simple CLI for looking up IP adresses

github: https://github.com/eletrixtime/iplookup-cli
'''

import sys
import requests
from colorama import Fore, Back, Style, init
import re
import socket

init(autoreset=True)  
_DEFAULTPROVIDER = "ip-api"

class Utils():
    def url_(r):
        regex = r'^([a-zA-Z0-9-]+\.)+[a-z]{2,}$'
        if re.match(regex, r):
            return socket.gethostbyname(r)
        else:
            return False

class Provider:
    def __init__(self, ip):
        self.ip = ip
        self.provider = _DEFAULTPROVIDER
    def look(self):
        try:
            if self.provider == "ip-api":
                return self.ip_api()    
        except:
            print("Error: Unknown provider OR error with provider")
        
    def ip_api(self):
        
        x = requests.get('http://ip-api.com/json/'+self.ip)
        if x.status_code != 200:
            print("Error: ip-api.com returned an error")
            return None
        return {
            "ip": x.json()["query"],
            "country": x.json()["country"],
            "countryCode": x.json()["countryCode"],
            "region": x.json()["region"],
            "regionName": x.json()["regionName"],
            "city": x.json()["city"],
            "zip": x.json()["zip"],
            "lat": x.json()["lat"],
            "lon": x.json()["lon"],
            "timezone": x.json()["timezone"],
            "isp": x.json()["isp"],
            "org": x.json()["org"],
            "as": x.json()["as"],
            "provider_used": self.provider
        }


def beautiful_show(data):
    print(f"{Fore.YELLOW}{Back.BLACK}{Style.BRIGHT}🔍 ==== Result of lookup ({data['ip']}) via {data['provider_used']} ===={Style.RESET_ALL}")
    print(f"{Fore.CYAN}🌍 Country:{Style.RESET_ALL} {data['country']} ({data['countryCode']})")
    print(f"    -{Fore.CYAN}🏙  Region:{Style.RESET_ALL} {data['region']} ({data['regionName']})")
    print(f"    -{Fore.CYAN}🏙  City:{Style.RESET_ALL} {data['city']}")
    print(f"{Fore.CYAN}📮  Zip:{Style.RESET_ALL} {data['zip']}")
    print(f"    -{Fore.GREEN}📍  Latitude:{Style.RESET_ALL} {data['lat']}")
    print(f"    -{Fore.GREEN}📍  Longitude:{Style.RESET_ALL} {data['lon']}")
    print(f"    -{Fore.MAGENTA}⏰  Timezone:{Style.RESET_ALL} {data['timezone']}")
    print(f"{Fore.BLUE}📶  ISP:{Style.RESET_ALL} {data['isp']}")
    print(f"    -{Fore.BLUE}🏢  Organization:{Style.RESET_ALL} {data['org']}")
    print(f"    -{Fore.BLUE}🖥  AS:{Style.RESET_ALL} {data['as']}")
    print(f"{Fore.YELLOW}{Back.BLACK}{Style.BRIGHT}🛑 ==== End of lookup ({data['ip']}) via {data['provider_used']} ===={Style.RESET_ALL}")

def main():
    if len(sys.argv) < 2:
        print("Usage: iplookup <ip>")
    else:
        ip = sys.argv[1]
        if Utils.url_(ip) != False:
            ip = Utils.url_(ip)
        else:
            pass

        if len(sys.argv) > 2:
            provider = sys.argv[2]
        else:
            provider = _DEFAULTPROVIDER
        beautiful_show(Provider(ip).look())
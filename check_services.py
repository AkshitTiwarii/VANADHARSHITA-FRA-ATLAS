#!/usr/bin/env python3
"""Quick service status check for all FRA services"""

import requests
from colorama import init, Fore, Style

init(autoreset=True)

services = [
    {
        "name": "🤖 AI Service",
        "url": "http://localhost:8000/health",
        "port": 8000
    },
    {
        "name": "🔗 Blockchain Service",
        "url": "http://localhost:8001/health",
        "port": 8001
    },
    {
        "name": "🐍 Backend API",
        "url": "http://127.0.0.1:3001/health",
        "port": 3001
    },
    {
        "name": "⚛️  Frontend",
        "url": "http://localhost:3000",
        "port": 3000
    }
]

print(f"\n{Fore.CYAN}{'='*60}")
print(f"{Fore.CYAN}   FRA ATLAS - SERVICE STATUS CHECK")
print(f"{Fore.CYAN}{'='*60}\n")

all_online = True

for service in services:
    try:
        response = requests.get(service['url'], timeout=5)
        if response.status_code == 200:
            print(f"{Fore.GREEN}✅ {service['name']} - ONLINE (Port {service['port']})")
        else:
            print(f"{Fore.YELLOW}⚠️  {service['name']} - RUNNING but returned {response.status_code}")
            all_online = False
    except requests.exceptions.ConnectionError:
        print(f"{Fore.RED}❌ {service['name']} - OFFLINE (Port {service['port']})")
        all_online = False
    except Exception as e:
        print(f"{Fore.RED}❌ {service['name']} - ERROR: {str(e)}")
        all_online = False

print(f"\n{Fore.CYAN}{'='*60}")

if all_online:
    print(f"{Fore.GREEN}✨ ALL SERVICES ARE ONLINE AND READY!")
    print(f"\n{Fore.WHITE}🌐 Access Points:")
    print(f"   - Frontend: {Fore.CYAN}http://localhost:3000")
    print(f"   - AI Service API: {Fore.CYAN}http://localhost:8000")
    print(f"   - Backend API: {Fore.CYAN}http://127.0.0.1:3001")
    print(f"   - Blockchain: {Fore.CYAN}http://localhost:8001")
else:
    print(f"{Fore.YELLOW}⚠️  SOME SERVICES ARE NOT RUNNING")
    print(f"\n{Fore.WHITE}💡 To start all services, run:")
    print(f"   {Fore.CYAN}.\\START_FIXED_SERVICES.ps1")

print(f"{Fore.CYAN}{'='*60}\n")

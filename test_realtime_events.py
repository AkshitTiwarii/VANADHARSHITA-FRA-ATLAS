"""
Test script for Real-time Officer Monitoring System
Demonstrates SSE connection and event reception
"""

import requests
import json
import time
import threading
from sseclient import SSEClient  # pip install sseclient-py

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def listen_to_events(officer_name="Officer-1"):
    """Connect to SSE endpoint and listen for real-time events"""
    print(f"\n{Colors.CYAN}📡 {officer_name} connecting to real-time events...{Colors.END}")
    
    try:
        url = "http://localhost:8000/api/officer/realtime-events"
        messages = SSEClient(url)
        
        print(f"{Colors.GREEN}✅ {officer_name} connected!{Colors.END}\n")
        print(f"{Colors.BOLD}{'='*80}{Colors.END}")
        print(f"{Colors.BOLD}Waiting for events... (Press Ctrl+C to stop){Colors.END}")
        print(f"{Colors.BOLD}{'='*80}{Colors.END}\n")
        
        for msg in messages:
            if msg.data:
                try:
                    event = json.loads(msg.data)
                    
                    # Color-code based on event type
                    if "verified" in event["event_type"] or "approved" in event["event_type"]:
                        color = Colors.GREEN
                        icon = "✅"
                    elif "failed" in event["event_type"] or "contradiction" in event["event_type"]:
                        color = Colors.RED
                        icon = "❌"
                    elif "started" in event["event_type"]:
                        color = Colors.BLUE
                        icon = "🔄"
                    else:
                        color = Colors.YELLOW
                        icon = "📡"
                    
                    # Print formatted event
                    print(f"{color}{icon} [{event['timestamp']}]{Colors.END}")
                    print(f"   {Colors.BOLD}Event:{Colors.END} {event['event_type']}")
                    print(f"   {Colors.BOLD}Workflow:{Colors.END} {event['workflow_id']}")
                    print(f"   {Colors.BOLD}Message:{Colors.END} {event['data'].get('message', 'N/A')}")
                    
                    # Show additional details based on event type
                    if event['event_type'] == 'blockchain_verified':
                        print(f"   {Colors.CYAN}Transaction:{Colors.END} {event['data'].get('transaction_id')}")
                        print(f"   {Colors.CYAN}Block:{Colors.END} {event['data'].get('block_number')}")
                    elif event['event_type'] == 'location_verified':
                        print(f"   {Colors.CYAN}NDVI:{Colors.END} {event['data'].get('ndvi')}")
                        print(f"   {Colors.CYAN}Land Type:{Colors.END} {event['data'].get('land_type')}")
                        print(f"   {Colors.CYAN}Match Score:{Colors.END} {event['data'].get('match_score')}%")
                    elif event['event_type'] == 'dss_evaluation_complete':
                        print(f"   {Colors.CYAN}DSS Score:{Colors.END} {event['data'].get('score')}/100")
                        print(f"   {Colors.CYAN}Recommendation:{Colors.END} {event['data'].get('recommendation')}")
                    
                    print(f"{Colors.BOLD}{'-'*80}{Colors.END}\n")
                    
                except json.JSONDecodeError:
                    pass
                    
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}👋 {officer_name} disconnecting...{Colors.END}")
    except Exception as e:
        print(f"{Colors.RED}❌ Error: {e}{Colors.END}")
        print(f"{Colors.YELLOW}Make sure AI service is running on http://localhost:8000{Colors.END}")

def get_recent_events():
    """Fetch recent events from history endpoint"""
    try:
        response = requests.get("http://localhost:8000/api/officer/recent-events")
        if response.status_code == 200:
            data = response.json()
            print(f"\n{Colors.CYAN}📜 Recent Events History:{Colors.END}")
            print(f"{Colors.BOLD}Total events: {data['count']}{Colors.END}\n")
            
            for event in data['events'][-10:]:  # Show last 10
                print(f"  [{event['timestamp']}] {event['event_type']}")
                print(f"    → {event['data'].get('message', 'N/A')}\n")
        else:
            print(f"{Colors.RED}❌ Failed to fetch events: {response.status_code}{Colors.END}")
    except Exception as e:
        print(f"{Colors.RED}❌ Error: {e}{Colors.END}")

def submit_test_document():
    """Submit a test document to trigger workflow events"""
    print(f"\n{Colors.BLUE}📤 Submitting test document...{Colors.END}")
    
    try:
        # Create a dummy text file as test document
        test_file_content = b"FOREST RIGHTS CLAIM\nName: Test User\nLocation: Sundarbans\nDate: 2025-01-17"
        
        files = {'file': ('test_claim.txt', test_file_content, 'text/plain')}
        data = {
            'applicant_name': 'Test User',
            'applicant_location': 'Sundarbans, West Bengal',
            'latitude': '21.9497',
            'longitude': '88.8872',
            'language': 'eng'
        }
        
        response = requests.post(
            'http://localhost:8000/api/document/comprehensive-verification',
            files=files,
            data=data
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"{Colors.GREEN}✅ Document submitted successfully!{Colors.END}")
            print(f"   Workflow ID: {result['workflow_id']}")
            print(f"   Status: {result['status']}")
        else:
            print(f"{Colors.RED}❌ Submission failed: {response.status_code}{Colors.END}")
            
    except Exception as e:
        print(f"{Colors.RED}❌ Error: {e}{Colors.END}")

def start_multiple_officers(count=3):
    """Start multiple officer connections to test concurrent streaming"""
    print(f"\n{Colors.BOLD}🚀 Starting {count} officer connections...{Colors.END}")
    
    threads = []
    for i in range(count):
        thread = threading.Thread(
            target=listen_to_events,
            args=(f"Officer-{i+1}",),
            daemon=True
        )
        thread.start()
        threads.append(thread)
        time.sleep(0.5)  # Stagger connections
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}👋 Shutting down all officers...{Colors.END}")

if __name__ == "__main__":
    import sys
    
    print(f"""
{Colors.BOLD}{Colors.CYAN}
╔═══════════════════════════════════════════════════════════╗
║        Real-time Officer Monitoring - Test Suite         ║
╚═══════════════════════════════════════════════════════════╝
{Colors.END}
    """)
    
    if len(sys.argv) < 2:
        print(f"{Colors.YELLOW}Usage:{Colors.END}")
        print(f"  python test_realtime_events.py listen          - Listen to events (single officer)")
        print(f"  python test_realtime_events.py multi           - Start multiple officers (3)")
        print(f"  python test_realtime_events.py history         - View recent events")
        print(f"  python test_realtime_events.py submit          - Submit test document")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "listen":
        listen_to_events()
    elif command == "multi":
        start_multiple_officers(3)
    elif command == "history":
        get_recent_events()
    elif command == "submit":
        submit_test_document()
    else:
        print(f"{Colors.RED}❌ Unknown command: {command}{Colors.END}")

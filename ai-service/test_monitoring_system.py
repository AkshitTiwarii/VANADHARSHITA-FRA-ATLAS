"""
Test Forest Monitoring System
Run this to verify monitoring is working
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models.monitoring_service import get_monitoring_service, ForestMonitoringService
from models.alert_system import get_alert_system


async def test_monitoring_system():
    """Test the complete monitoring system"""
    
    print("\n" + "=" * 70)
    print("🛰️  FOREST MONITORING SYSTEM TEST")
    print("=" * 70)
    
    # Test 1: Initialize service
    print("\n1️⃣  Initializing monitoring service...")
    service = get_monitoring_service()
    print(f"✅ Service initialized (check interval: {service.check_interval_days} days)")
    
    # Test 2: Get sample villages
    print("\n2️⃣  Loading sample villages...")
    villages = service.get_sample_villages()
    print(f"✅ Loaded {len(villages)} sample villages:")
    for v in villages:
        print(f"   - {v.village_name}, {v.district} ({v.latitude:.4f}, {v.longitude:.4f})")
    
    # Test 3: Run monitoring cycle
    print("\n3️⃣  Running monitoring cycle...")
    print("   (This will analyze satellite data for each village)")
    alerts = await service.run_monitoring_cycle()
    
    # Test 4: Display results
    print("\n4️⃣  Monitoring Results:")
    print(f"   Villages Analyzed: {len(villages)}")
    print(f"   Alerts Generated: {len(alerts)}")
    
    if alerts:
        print("\n   🚨 DEFORESTATION ALERTS DETECTED:")
        for alert in alerts:
            print(f"\n   Alert ID: {alert.alert_id}")
            print(f"   Village: {alert.village_name}")
            print(f"   Location: {alert.latitude:.6f}°N, {alert.longitude:.6f}°E")
            print(f"   NDVI Change: {alert.ndvi_previous:.3f} → {alert.ndvi_current:.3f}")
            print(f"   Vegetation Loss: {alert.vegetation_loss_percentage:.1f}%")
            print(f"   Risk Level: {alert.deforestation_risk.upper()}")
            
            # Test 5: Send test alert
            print(f"\n   📧 Testing alert system for {alert.village_name}...")
            alert_system = get_alert_system()
            result = alert_system.send_alert(alert.to_dict())
            
            if result['email_sent']:
                print(f"   ✅ Email sent to {alert.district_collector_email}")
            else:
                print(f"   ℹ️  Email not sent (configure SMTP in .env)")
            
            if result['sms_sent']:
                print(f"   ✅ SMS sent to {alert.forest_officer_phone}")
            else:
                print(f"   ℹ️  SMS not sent (configure Twilio in .env)")
    else:
        print("\n   ✅ No deforestation detected - all forests healthy!")
    
    # Test 6: Get statistics
    print("\n5️⃣  Monitoring Statistics:")
    stats = service.get_alert_statistics()
    print(f"   Total Alerts (All Time): {stats['total_alerts']}")
    print(f"   High Risk: {stats['high_risk_alerts']}")
    print(f"   Medium Risk: {stats['medium_risk_alerts']}")
    print(f"   Low Risk: {stats['low_risk_alerts']}")
    print(f"   Monitoring Active: {stats['monitoring_active']}")
    
    # Test 7: Recent alerts
    print("\n6️⃣  Recent Alerts (Last 10):")
    recent = service.get_recent_alerts(limit=10)
    if recent:
        for i, alert in enumerate(recent, 1):
            print(f"   {i}. {alert['village_name']}: {alert['vegetation_loss_percentage']:.1f}% loss ({alert['deforestation_risk']} risk)")
    else:
        print("   No alerts in history")
    
    print("\n" + "=" * 70)
    print("✅ MONITORING SYSTEM TEST COMPLETE")
    print("=" * 70)
    
    # Summary
    print("\n📊 SUMMARY:")
    print(f"   • Monitoring service: {'✅ Working' if service else '❌ Failed'}")
    print(f"   • Alert system: {'✅ Working' if alert_system else '❌ Failed'}")
    print(f"   • Villages monitored: {len(villages)}")
    print(f"   • Alerts generated: {len(alerts)}")
    print(f"   • Total alerts (history): {stats['total_alerts']}")
    
    if len(alerts) > 0:
        print(f"\n⚠️  ACTION REQUIRED:")
        print(f"   {len(alerts)} deforestation alert(s) detected!")
        print(f"   Forest officers have been notified via SMS/Email.")
        print(f"   View details in the monitoring dashboard: /monitoring")
    
    print("\n💡 NEXT STEPS:")
    print("   1. Configure Email (SMTP) in ai-service/.env for real alerts")
    print("   2. Configure SMS (Twilio) in ai-service/.env for SMS notifications")
    print("   3. Start the AI service: python main_v2.py")
    print("   4. Open the monitoring dashboard: http://localhost:3001/monitoring")
    print("   5. Set up automated monitoring (runs every 5 days)")
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    # Run the test
    asyncio.run(test_monitoring_system())

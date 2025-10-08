"""
Real-Time Forest Monitoring Service
Automatically monitors all FRA villages for deforestation using satellite data
Runs every 5 days and sends alerts when vegetation loss is detected
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json
from dataclasses import dataclass, asdict
import schedule
import time

from .satellite_analyzer import get_satellite_analyzer

logger = logging.getLogger(__name__)


@dataclass
class VillageMonitoringData:
    """Data structure for village monitoring"""
    village_id: str
    village_name: str
    latitude: float
    longitude: float
    radius: int = 500  # meters
    last_checked: Optional[str] = None
    last_ndvi: Optional[float] = None
    district: Optional[str] = None
    state: Optional[str] = None
    forest_officer_phone: Optional[str] = None
    district_collector_email: Optional[str] = None


@dataclass
class DeforestationAlert:
    """Alert data structure"""
    alert_id: str
    village_id: str
    village_name: str
    latitude: float
    longitude: float
    ndvi_current: float
    ndvi_previous: float
    vegetation_loss_percentage: float
    deforestation_risk: str  # low, medium, high
    detection_date: str
    alert_sent: bool = False
    district: Optional[str] = None
    state: Optional[str] = None
    forest_officer_phone: Optional[str] = None
    district_collector_email: Optional[str] = None
    
    def to_dict(self):
        return asdict(self)


class ForestMonitoringService:
    """
    Automated forest monitoring service
    Monitors all FRA villages for deforestation using satellite analysis
    """
    
    def __init__(self, check_interval_days: int = 5):
        self.check_interval_days = check_interval_days
        self.satellite_analyzer = get_satellite_analyzer()
        self.alerts: List[DeforestationAlert] = []
        self.monitoring_active = False
        
        # Thresholds for alerts
        self.VEGETATION_LOSS_THRESHOLD = 0.10  # 10% loss triggers alert
        self.HIGH_RISK_THRESHOLD = 0.30  # 30% loss = HIGH RISK
        self.MEDIUM_RISK_THRESHOLD = 0.15  # 15% loss = MEDIUM RISK
        
        logger.info(f"Forest Monitoring Service initialized (check every {check_interval_days} days)")
    
    async def analyze_village(self, village: VillageMonitoringData) -> Optional[DeforestationAlert]:
        """
        Analyze a single village for deforestation
        Returns alert if vegetation loss detected, None otherwise
        """
        try:
            logger.info(f"Analyzing village: {village.village_name} ({village.latitude}, {village.longitude})")
            
            # Perform satellite analysis
            result = self.satellite_analyzer.analyze(
                lat=village.latitude,
                lon=village.longitude,
                radius=village.radius
            )
            
            if not result or not result.get('success'):
                logger.warning(f"Analysis failed for {village.village_name}")
                return None
            
            # Extract NDVI data
            current_ndvi = result.get('ndvi', {}).get('value', 0)
            change_detection = result.get('change_detection', {})
            vegetation_loss = change_detection.get('vegetation_loss', False)
            change_percentage = abs(change_detection.get('change_percentage', 0))
            
            # Check if we have previous NDVI for comparison
            if village.last_ndvi is None:
                # First time monitoring this village - store baseline
                logger.info(f"Baseline NDVI for {village.village_name}: {current_ndvi:.3f}")
                return None
            
            # Calculate vegetation loss
            ndvi_drop = village.last_ndvi - current_ndvi
            loss_percentage = (ndvi_drop / village.last_ndvi) * 100 if village.last_ndvi > 0 else 0
            
            # Check if loss exceeds threshold
            if vegetation_loss and loss_percentage >= (self.VEGETATION_LOSS_THRESHOLD * 100):
                # Determine risk level
                if loss_percentage >= (self.HIGH_RISK_THRESHOLD * 100):
                    risk_level = "high"
                elif loss_percentage >= (self.MEDIUM_RISK_THRESHOLD * 100):
                    risk_level = "medium"
                else:
                    risk_level = "low"
                
                # Create alert
                alert = DeforestationAlert(
                    alert_id=f"ALERT-{village.village_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    village_id=village.village_id,
                    village_name=village.village_name,
                    latitude=village.latitude,
                    longitude=village.longitude,
                    ndvi_current=current_ndvi,
                    ndvi_previous=village.last_ndvi,
                    vegetation_loss_percentage=loss_percentage,
                    deforestation_risk=risk_level,
                    detection_date=datetime.now().isoformat(),
                    district=village.district,
                    state=village.state,
                    forest_officer_phone=village.forest_officer_phone,
                    district_collector_email=village.district_collector_email
                )
                
                logger.warning(
                    f"🚨 DEFORESTATION ALERT: {village.village_name} - "
                    f"NDVI dropped from {village.last_ndvi:.3f} to {current_ndvi:.3f} "
                    f"({loss_percentage:.1f}% loss) - Risk: {risk_level.upper()}"
                )
                
                return alert
            else:
                logger.info(
                    f"✅ {village.village_name} - No significant change "
                    f"(NDVI: {current_ndvi:.3f}, Change: {loss_percentage:.1f}%)"
                )
                return None
                
        except Exception as e:
            logger.error(f"Error analyzing village {village.village_name}: {e}")
            return None
    
    async def monitor_all_villages(self, villages: List[VillageMonitoringData]) -> List[DeforestationAlert]:
        """
        Monitor all villages and return list of alerts
        """
        logger.info(f"Starting monitoring cycle for {len(villages)} villages...")
        alerts = []
        
        # Analyze villages in parallel (with rate limiting)
        batch_size = 10  # Analyze 10 villages at a time
        for i in range(0, len(villages), batch_size):
            batch = villages[i:i + batch_size]
            tasks = [self.analyze_village(village) for village in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, DeforestationAlert):
                    alerts.append(result)
                    self.alerts.append(result)
            
            # Rate limiting - wait 5 seconds between batches
            if i + batch_size < len(villages):
                await asyncio.sleep(5)
        
        logger.info(f"Monitoring cycle complete. {len(alerts)} alerts generated.")
        return alerts
    
    def get_sample_villages(self) -> List[VillageMonitoringData]:
        """
        Get sample villages for demonstration
        In production, this would fetch from database
        """
        return [
            VillageMonitoringData(
                village_id="VIL001",
                village_name="Bhamragad",
                latitude=18.9217285,
                longitude=77.0038332,
                district="Gadchiroli",
                state="Maharashtra",
                forest_officer_phone="+91-9876543210",
                district_collector_email="collector@gadchiroli.gov.in",
                last_ndvi=0.78  # Baseline from previous check
            ),
            VillageMonitoringData(
                village_id="VIL002",
                village_name="Etapalli",
                latitude=19.0123456,
                longitude=80.5678901,
                district="Gadchiroli",
                state="Maharashtra",
                forest_officer_phone="+91-9876543211",
                district_collector_email="collector@gadchiroli.gov.in",
                last_ndvi=0.82
            ),
            VillageMonitoringData(
                village_id="VIL003",
                village_name="Korchi",
                latitude=19.5234567,
                longitude=79.8765432,
                district="Gadchiroli",
                state="Maharashtra",
                forest_officer_phone="+91-9876543212",
                district_collector_email="collector@gadchiroli.gov.in",
                last_ndvi=0.75
            ),
            # Add more sample villages
            VillageMonitoringData(
                village_id="VIL004",
                village_name="Dhanora",
                latitude=18.3456789,
                longitude=79.1234567,
                district="Gadchiroli",
                state="Maharashtra",
                forest_officer_phone="+91-9876543213",
                district_collector_email="collector@gadchiroli.gov.in",
                last_ndvi=0.68
            ),
            VillageMonitoringData(
                village_id="VIL005",
                village_name="Aheri",
                latitude=19.0987654,
                longitude=80.2345678,
                district="Gadchiroli",
                state="Maharashtra",
                forest_officer_phone="+91-9876543214",
                district_collector_email="collector@gadchiroli.gov.in",
                last_ndvi=0.85
            ),
        ]
    
    async def run_monitoring_cycle(self):
        """
        Run a single monitoring cycle
        """
        logger.info("=" * 60)
        logger.info(f"🛰️  FOREST MONITORING CYCLE STARTED - {datetime.now().isoformat()}")
        logger.info("=" * 60)
        
        # Get villages to monitor (in production, fetch from database)
        villages = self.get_sample_villages()
        logger.info(f"Monitoring {len(villages)} villages...")
        
        # Monitor all villages
        alerts = await self.monitor_all_villages(villages)
        
        # Log results
        logger.info("=" * 60)
        logger.info(f"📊 MONITORING CYCLE COMPLETE")
        logger.info(f"Villages Checked: {len(villages)}")
        logger.info(f"Alerts Generated: {len(alerts)}")
        
        if alerts:
            logger.warning(f"🚨 {len(alerts)} DEFORESTATION ALERTS:")
            for alert in alerts:
                logger.warning(
                    f"  - {alert.village_name}: {alert.vegetation_loss_percentage:.1f}% loss "
                    f"(Risk: {alert.deforestation_risk.upper()})"
                )
        else:
            logger.info("✅ No deforestation detected in monitored villages")
        
        logger.info("=" * 60)
        
        return alerts
    
    def get_recent_alerts(self, limit: int = 50) -> List[Dict]:
        """Get recent alerts"""
        return [alert.to_dict() for alert in self.alerts[-limit:]]
    
    def get_alert_statistics(self) -> Dict:
        """Get monitoring statistics"""
        total_alerts = len(self.alerts)
        high_risk = sum(1 for alert in self.alerts if alert.deforestation_risk == "high")
        medium_risk = sum(1 for alert in self.alerts if alert.deforestation_risk == "medium")
        low_risk = sum(1 for alert in self.alerts if alert.deforestation_risk == "low")
        
        return {
            "total_alerts": total_alerts,
            "high_risk_alerts": high_risk,
            "medium_risk_alerts": medium_risk,
            "low_risk_alerts": low_risk,
            "last_check": datetime.now().isoformat(),
            "monitoring_active": self.monitoring_active
        }


# Global monitoring service instance
_monitoring_service: Optional[ForestMonitoringService] = None


def get_monitoring_service() -> ForestMonitoringService:
    """Get or create monitoring service instance"""
    global _monitoring_service
    if _monitoring_service is None:
        _monitoring_service = ForestMonitoringService(check_interval_days=5)
    return _monitoring_service


async def run_scheduled_monitoring():
    """
    Run monitoring on schedule (every 5 days)
    This can be run as a background task or separate cron job
    """
    service = get_monitoring_service()
    service.monitoring_active = True
    
    try:
        while service.monitoring_active:
            # Run monitoring cycle
            await service.run_monitoring_cycle()
            
            # Wait for next cycle (5 days = 432000 seconds)
            wait_seconds = service.check_interval_days * 24 * 60 * 60
            logger.info(f"💤 Next monitoring cycle in {service.check_interval_days} days...")
            
            # For demo purposes, you can reduce this to 1 hour or 5 minutes
            # wait_seconds = 3600  # 1 hour for testing
            # wait_seconds = 300   # 5 minutes for demo
            
            await asyncio.sleep(wait_seconds)
    except Exception as e:
        logger.error(f"Monitoring service error: {e}")
        service.monitoring_active = False


if __name__ == "__main__":
    # Test the monitoring service
    async def test_monitoring():
        service = get_monitoring_service()
        alerts = await service.run_monitoring_cycle()
        
        print("\n" + "=" * 60)
        print("📋 MONITORING TEST RESULTS")
        print("=" * 60)
        print(f"Alerts Generated: {len(alerts)}")
        
        if alerts:
            print("\n🚨 ALERTS:")
            for alert in alerts:
                print(f"\n  Village: {alert.village_name}")
                print(f"  Location: {alert.latitude:.6f}°N, {alert.longitude:.6f}°E")
                print(f"  NDVI: {alert.ndvi_previous:.3f} → {alert.ndvi_current:.3f}")
                print(f"  Loss: {alert.vegetation_loss_percentage:.1f}%")
                print(f"  Risk: {alert.deforestation_risk.upper()}")
        else:
            print("✅ No alerts - all villages have healthy vegetation")
        
        print("\n" + "=" * 60)
        
        # Get statistics
        stats = service.get_alert_statistics()
        print("\n📊 STATISTICS:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        print("=" * 60)
    
    # Run test
    asyncio.run(test_monitoring())

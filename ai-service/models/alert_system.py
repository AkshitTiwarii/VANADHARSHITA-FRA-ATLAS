"""
Alert System for Deforestation Detection
Sends SMS and Email alerts to Forest Officers and District Collectors
"""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict
from datetime import datetime
import os

logger = logging.getLogger(__name__)


class AlertSystem:
    """
    Handles sending alerts via SMS and Email
    """
    
    def __init__(self):
        # Email configuration (from environment variables)
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.email_sender = os.getenv('EMAIL_SENDER', 'fra-atlas@example.com')
        self.email_password = os.getenv('EMAIL_PASSWORD', '')
        
        # SMS configuration (Twilio or AWS SNS)
        self.sms_enabled = os.getenv('SMS_ENABLED', 'false').lower() == 'true'
        self.twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID', '')
        self.twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN', '')
        self.twilio_phone_number = os.getenv('TWILIO_PHONE_NUMBER', '')
        
        logger.info(f"Alert System initialized (SMS: {self.sms_enabled}, Email: {bool(self.email_password)})")
    
    def send_email_alert(
        self,
        recipient_email: str,
        village_name: str,
        latitude: float,
        longitude: float,
        ndvi_previous: float,
        ndvi_current: float,
        vegetation_loss_percentage: float,
        deforestation_risk: str,
        district: Optional[str] = None,
        state: Optional[str] = None,
        alert_id: Optional[str] = None
    ) -> bool:
        """
        Send email alert to District Collector
        """
        try:
            if not self.email_password:
                logger.warning("Email password not configured - skipping email alert")
                logger.info(f"[DEMO] Would send email to: {recipient_email}")
                logger.info(f"[DEMO] Subject: 🚨 Deforestation Alert - {village_name}")
                return False
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"🚨 Deforestation Alert - {village_name} ({deforestation_risk.upper()} RISK)"
            msg['From'] = self.email_sender
            msg['To'] = recipient_email
            
            # Risk color
            risk_colors = {
                'high': '#dc2626',  # Red
                'medium': '#f59e0b',  # Orange
                'low': '#eab308'  # Yellow
            }
            risk_color = risk_colors.get(deforestation_risk, '#6b7280')
            
            # HTML email body
            html = f"""
            <html>
              <head>
                <style>
                  body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                  .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                  .header {{ background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%); 
                            color: white; padding: 30px; border-radius: 8px 8px 0 0; }}
                  .alert-box {{ background: {risk_color}; color: white; padding: 20px; 
                                margin: 20px 0; border-radius: 8px; text-align: center; }}
                  .details {{ background: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                  .detail-row {{ display: flex; justify-content: space-between; padding: 10px 0; 
                                 border-bottom: 1px solid #e5e7eb; }}
                  .label {{ font-weight: 600; color: #6b7280; }}
                  .value {{ color: #111827; font-weight: 500; }}
                  .map-button {{ display: inline-block; background: #3b82f6; color: white; 
                                 padding: 12px 24px; text-decoration: none; border-radius: 6px; 
                                 margin: 20px 0; font-weight: 600; }}
                  .footer {{ text-align: center; color: #6b7280; font-size: 12px; margin-top: 30px; }}
                </style>
              </head>
              <body>
                <div class="container">
                  <div class="header">
                    <h1 style="margin: 0; font-size: 24px;">🛰️ FRA Atlas</h1>
                    <p style="margin: 10px 0 0 0; opacity: 0.9;">Forest Rights Monitoring System</p>
                  </div>
                  
                  <div class="alert-box">
                    <h2 style="margin: 0 0 10px 0;">⚠️ DEFORESTATION ALERT</h2>
                    <p style="margin: 0; font-size: 18px; font-weight: 600;">
                      {deforestation_risk.upper()} RISK DETECTED
                    </p>
                  </div>
                  
                  <div class="details">
                    <h3 style="margin-top: 0; color: #111827;">Location Details</h3>
                    
                    <div class="detail-row">
                      <span class="label">Village:</span>
                      <span class="value">{village_name}</span>
                    </div>
                    
                    {f'''
                    <div class="detail-row">
                      <span class="label">District:</span>
                      <span class="value">{district}</span>
                    </div>
                    ''' if district else ''}
                    
                    {f'''
                    <div class="detail-row">
                      <span class="label">State:</span>
                      <span class="value">{state}</span>
                    </div>
                    ''' if state else ''}
                    
                    <div class="detail-row">
                      <span class="label">GPS Coordinates:</span>
                      <span class="value">{latitude:.6f}°N, {longitude:.6f}°E</span>
                    </div>
                    
                    <div class="detail-row">
                      <span class="label">Detection Date:</span>
                      <span class="value">{datetime.now().strftime('%B %d, %Y at %H:%M IST')}</span>
                    </div>
                    
                    {f'''
                    <div class="detail-row">
                      <span class="label">Alert ID:</span>
                      <span class="value">{alert_id}</span>
                    </div>
                    ''' if alert_id else ''}
                  </div>
                  
                  <div class="details">
                    <h3 style="margin-top: 0; color: #111827;">Satellite Analysis</h3>
                    
                    <div class="detail-row">
                      <span class="label">NDVI (Previous):</span>
                      <span class="value" style="color: #16a34a;">{ndvi_previous:.3f} (Healthy Forest)</span>
                    </div>
                    
                    <div class="detail-row">
                      <span class="label">NDVI (Current):</span>
                      <span class="value" style="color: {risk_color};">{ndvi_current:.3f} (Degraded)</span>
                    </div>
                    
                    <div class="detail-row">
                      <span class="label">Vegetation Loss:</span>
                      <span class="value" style="color: {risk_color}; font-size: 18px; font-weight: 700;">
                        {vegetation_loss_percentage:.1f}%
                      </span>
                    </div>
                    
                    <div class="detail-row">
                      <span class="label">Risk Level:</span>
                      <span class="value" style="color: {risk_color}; font-weight: 700; text-transform: uppercase;">
                        {deforestation_risk}
                      </span>
                    </div>
                  </div>
                  
                  <div style="text-align: center;">
                    <a href="https://fra-atlas.example.com/map?lat={latitude}&lng={longitude}" 
                       class="map-button">
                      📍 View Location on Interactive Map
                    </a>
                  </div>
                  
                  <div style="background: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin: 20px 0; border-radius: 4px;">
                    <p style="margin: 0; color: #92400e; font-weight: 600;">⚡ Immediate Action Required</p>
                    <p style="margin: 10px 0 0 0; color: #78350f;">
                      Satellite imagery indicates significant vegetation loss in this FRA territory. 
                      Please conduct an immediate field inspection to verify the cause and take necessary action.
                    </p>
                  </div>
                  
                  <div style="background: #dbeafe; border-left: 4px solid #3b82f6; padding: 15px; margin: 20px 0; border-radius: 4px;">
                    <p style="margin: 0; color: #1e40af; font-weight: 600;">📋 Recommended Actions:</p>
                    <ul style="margin: 10px 0 0 0; color: #1e3a8a; padding-left: 20px;">
                      <li>Deploy forest guard to the location immediately</li>
                      <li>Document the current condition with photographs</li>
                      <li>Identify the cause of vegetation loss (logging, fire, encroachment)</li>
                      <li>File FIR if illegal activity is confirmed</li>
                      <li>Update the FRA Atlas system with findings</li>
                    </ul>
                  </div>
                  
                  <div class="footer">
                    <p>This is an automated alert from the FRA Atlas Forest Monitoring System.</p>
                    <p>Powered by Google Earth Engine Sentinel-2 satellite imagery (10m resolution).</p>
                    <p style="margin-top: 15px;">
                      <strong>FRA Atlas</strong> | Ministry of Tribal Affairs, Government of India<br>
                      For support: support@fra-atlas.gov.in | Tel: 1800-XXX-XXXX
                    </p>
                  </div>
                </div>
              </body>
            </html>
            """
            
            # Attach HTML content
            html_part = MIMEText(html, 'html')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_sender, self.email_password)
                server.send_message(msg)
            
            logger.info(f"✅ Email alert sent to {recipient_email} for {village_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
            return False
    
    def send_sms_alert(
        self,
        phone_number: str,
        village_name: str,
        vegetation_loss_percentage: float,
        deforestation_risk: str,
        latitude: float,
        longitude: float
    ) -> bool:
        """
        Send SMS alert to Forest Officer
        """
        try:
            if not self.sms_enabled or not self.twilio_auth_token:
                logger.warning("SMS not configured - skipping SMS alert")
                logger.info(f"[DEMO] Would send SMS to: {phone_number}")
                logger.info(f"[DEMO] Message: 🚨 Deforestation alert in {village_name}")
                return False
            
            # Import Twilio (optional dependency)
            from twilio.rest import Client
            
            # Create SMS message
            message_body = f"""
🚨 FRA DEFORESTATION ALERT

Village: {village_name}
Vegetation Loss: {vegetation_loss_percentage:.1f}%
Risk: {deforestation_risk.upper()}

Location: {latitude:.6f}°N, {longitude:.6f}°E

View map: https://fra-atlas.gov.in/map?lat={latitude}&lng={longitude}

Immediate field inspection required.

- FRA Atlas Monitoring System
            """.strip()
            
            # Send SMS via Twilio
            client = Client(self.twilio_account_sid, self.twilio_auth_token)
            message = client.messages.create(
                body=message_body,
                from_=self.twilio_phone_number,
                to=phone_number
            )
            
            logger.info(f"✅ SMS alert sent to {phone_number} (SID: {message.sid})")
            return True
            
        except ImportError:
            logger.warning("Twilio not installed. Install with: pip install twilio")
            logger.info(f"[DEMO] SMS message prepared for {phone_number}")
            return False
        except Exception as e:
            logger.error(f"Failed to send SMS alert: {e}")
            return False
    
    def send_alert(self, alert_data: Dict) -> Dict[str, bool]:
        """
        Send both email and SMS alerts
        Returns status of each notification
        """
        results = {
            'email_sent': False,
            'sms_sent': False
        }
        
        # Send email to District Collector
        if alert_data.get('district_collector_email'):
            results['email_sent'] = self.send_email_alert(
                recipient_email=alert_data['district_collector_email'],
                village_name=alert_data['village_name'],
                latitude=alert_data['latitude'],
                longitude=alert_data['longitude'],
                ndvi_previous=alert_data['ndvi_previous'],
                ndvi_current=alert_data['ndvi_current'],
                vegetation_loss_percentage=alert_data['vegetation_loss_percentage'],
                deforestation_risk=alert_data['deforestation_risk'],
                district=alert_data.get('district'),
                state=alert_data.get('state'),
                alert_id=alert_data.get('alert_id')
            )
        
        # Send SMS to Forest Officer
        if alert_data.get('forest_officer_phone'):
            results['sms_sent'] = self.send_sms_alert(
                phone_number=alert_data['forest_officer_phone'],
                village_name=alert_data['village_name'],
                vegetation_loss_percentage=alert_data['vegetation_loss_percentage'],
                deforestation_risk=alert_data['deforestation_risk'],
                latitude=alert_data['latitude'],
                longitude=alert_data['longitude']
            )
        
        return results


# Global alert system instance
_alert_system: Optional[AlertSystem] = None


def get_alert_system() -> AlertSystem:
    """Get or create alert system instance"""
    global _alert_system
    if _alert_system is None:
        _alert_system = AlertSystem()
    return _alert_system


if __name__ == "__main__":
    # Test the alert system
    alert_system = get_alert_system()
    
    test_alert = {
        'alert_id': 'ALERT-TEST-20251003',
        'village_name': 'Bhamragad',
        'district': 'Gadchiroli',
        'state': 'Maharashtra',
        'latitude': 18.9217285,
        'longitude': 77.0038332,
        'ndvi_previous': 0.78,
        'ndvi_current': 0.15,
        'vegetation_loss_percentage': 80.8,
        'deforestation_risk': 'high',
        'forest_officer_phone': '+91-9876543210',
        'district_collector_email': 'test@example.com'
    }
    
    print("\n" + "=" * 60)
    print("📧 TESTING ALERT SYSTEM")
    print("=" * 60)
    
    results = alert_system.send_alert(test_alert)
    
    print(f"\nEmail Sent: {'✅' if results['email_sent'] else '❌'}")
    print(f"SMS Sent: {'✅' if results['sms_sent'] else '❌'}")
    print("\n" + "=" * 60)

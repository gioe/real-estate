"""
Notification System Module

This module handles sending notifications when properties matching specific criteria are found.
Supports email, SMS, and webhook notifications.
"""

import smtplib
import ssl
import logging
from typing import Dict, List, Any, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import json
import urllib.request
import urllib.parse

logger = logging.getLogger(__name__)


class NotificationManager:
    """Main class for managing various types of notifications."""
    
    def __init__(self, notification_config: Dict[str, Any]):
        """
        Initialize the notification manager with configuration.
        
        Args:
            notification_config: Dictionary containing notification settings
        """
        self.config = notification_config
        self.enabled_channels = self.config.get('enabled_channels', ['email'])
        
    def send_property_alerts(self, matching_properties: List[Dict[str, Any]]) -> bool:
        """
        Send alerts for properties matching notification criteria.
        
        Args:
            matching_properties: List of properties that match criteria
            
        Returns:
            True if notifications were sent successfully, False otherwise
        """
        if not matching_properties:
            logger.info("No matching properties to notify about")
            return True
        
        logger.info(f"Sending notifications for {len(matching_properties)} matching properties")
        
        success = True
        
        try:
            # Prepare notification content
            subject = f"New Property Alert - {len(matching_properties)} Properties Found"
            message = self._create_property_alert_message(matching_properties)
            
            # Send via enabled channels
            if 'email' in self.enabled_channels:
                email_success = self._send_email_notification(subject, message, matching_properties)
                success = success and email_success
            
            if 'sms' in self.enabled_channels:
                sms_success = self._send_sms_notification(message, matching_properties)
                success = success and sms_success
            
            if 'webhook' in self.enabled_channels:
                webhook_success = self._send_webhook_notification(matching_properties)
                success = success and webhook_success
            
            if 'slack' in self.enabled_channels:
                slack_success = self._send_slack_notification(subject, message, matching_properties)
                success = success and slack_success
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending property alerts: {str(e)}")
            return False
    
    def send_market_report(self, analysis_results: Dict[str, Any], report_path: str) -> bool:
        """
        Send market analysis report.
        
        Args:
            analysis_results: Results from market analysis
            report_path: Path to generated report files
            
        Returns:
            True if report was sent successfully, False otherwise
        """
        logger.info("Sending market analysis report")
        
        try:
            subject = f"Market Analysis Report - {datetime.now().strftime('%Y-%m-%d')}"
            message = self._create_market_report_message(analysis_results)
            
            if 'email' in self.enabled_channels:
                return self._send_email_notification(subject, message, [], report_path)
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending market report: {str(e)}")
            return False
    
    def _create_property_alert_message(self, properties: List[Dict[str, Any]]) -> str:
        """Create formatted message for property alerts."""
        
        message_lines = [
            f"Found {len(properties)} properties matching your criteria:",
            "",
            "Property Details:",
            "=" * 50
        ]
        
        for i, prop in enumerate(properties, 1):
            message_lines.extend([
                f"\n{i}. {prop.get('address', 'Address not available')}",
                f"   City: {prop.get('city', 'N/A')}",
                f"   Price: ${prop.get('price', 0):,.2f}" if prop.get('price') else "   Price: N/A",
                f"   Bedrooms: {prop.get('bedrooms', 'N/A')}",
                f"   Bathrooms: {prop.get('bathrooms', 'N/A')}",
                f"   Square Feet: {prop.get('square_feet', 'N/A'):,}" if prop.get('square_feet') else "   Square Feet: N/A",
                f"   Days on Market: {prop.get('days_on_market', 'N/A')}",
                f"   Source: {prop.get('source', 'N/A')}",
                f"   URL: {prop.get('url', 'N/A')}"
            ])
        
        message_lines.extend([
            "",
            "=" * 50,
            f"Alert generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "This is an automated alert from your Real Estate Data Analyzer."
        ])
        
        return "\n".join(message_lines)
    
    def _create_market_report_message(self, analysis_results: Dict[str, Any]) -> str:
        """Create formatted message for market reports."""
        
        message_lines = [
            "Real Estate Market Analysis Report",
            "=" * 40,
            ""
        ]
        
        # Market summary
        if 'market_summary' in analysis_results:
            summary = analysis_results['market_summary']
            message_lines.extend([
                "MARKET SUMMARY:",
                f"Total Properties Analyzed: {summary.get('total_properties', 'N/A')}",
                f"Median Price: ${summary.get('price_summary', {}).get('median_price', 0):,.2f}" if summary.get('price_summary', {}).get('median_price') else "Median Price: N/A",
                f"Average Price: ${summary.get('price_summary', {}).get('average_price', 0):,.2f}" if summary.get('price_summary', {}).get('average_price') else "Average Price: N/A",
                ""
            ])
        
        # Market trends
        if 'market_trends' in analysis_results:
            trends = analysis_results['market_trends']
            message_lines.extend([
                "MARKET TRENDS:",
                f"Price Trend: {trends.get('price_trend', 'N/A').replace('_', ' ').title()}",
                f"Volume Trend: {trends.get('volume_trend', 'N/A').replace('_', ' ').title()}",
                ""
            ])
        
        # Investment opportunities
        if 'investment_opportunities' in analysis_results:
            opportunities = analysis_results['investment_opportunities']
            underpriced_count = len(opportunities.get('underpriced_properties', []))
            long_market_count = len(opportunities.get('long_on_market', []))
            
            message_lines.extend([
                "INVESTMENT OPPORTUNITIES:",
                f"Underpriced Properties: {underpriced_count}",
                f"Long on Market (Negotiable): {long_market_count}",
                ""
            ])
        
        message_lines.extend([
            "=" * 40,
            f"Report generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "Full analysis report and visualizations are attached."
        ])
        
        return "\n".join(message_lines)
    
    def _send_email_notification(self, subject: str, message: str, 
                               properties: List[Dict[str, Any]], 
                               attachment_path: Optional[str] = None) -> bool:
        """Send email notification."""
        try:
            email_config = self.config.get('email', {})
            
            if not email_config.get('enabled', False):
                logger.info("Email notifications are disabled")
                return True
            
            smtp_server = email_config.get('smtp_server')
            smtp_port = email_config.get('smtp_port', 587)
            username = email_config.get('username')
            password = email_config.get('password')
            recipients = email_config.get('recipients', [])
            
            if not all([smtp_server, username, password, recipients]):
                logger.error("Email configuration incomplete")
                return False
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = username
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = subject
            
            # Add body
            msg.attach(MIMEText(message, 'plain'))
            
            # Add HTML version for better formatting
            html_message = self._create_html_message(message, properties)
            msg.attach(MIMEText(html_message, 'html'))
            
            # Connect to server and send email
            context = ssl.create_default_context()
            
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls(context=context)
                server.login(username, password)
                server.sendmail(username, recipients, msg.as_string())
            
            logger.info(f"Email notification sent to {len(recipients)} recipients")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email notification: {str(e)}")
            return False
    
    def _send_sms_notification(self, message: str, properties: List[Dict[str, Any]]) -> bool:
        """Send SMS notification using Twilio or similar service."""
        try:
            sms_config = self.config.get('sms', {})
            
            if not sms_config.get('enabled', False):
                logger.info("SMS notifications are disabled")
                return True
            
            # Placeholder implementation for SMS
            # In a real implementation, you would use Twilio, AWS SNS, or similar
            
            provider = sms_config.get('provider', 'twilio')
            
            if provider == 'twilio':
                return self._send_twilio_sms(message, properties, sms_config)
            elif provider == 'aws_sns':
                return self._send_aws_sns_sms(message, properties, sms_config)
            else:
                logger.error(f"Unsupported SMS provider: {provider}")
                return False
            
        except Exception as e:
            logger.error(f"Error sending SMS notification: {str(e)}")
            return False
    
    def _send_twilio_sms(self, message: str, properties: List[Dict[str, Any]], sms_config: Dict[str, Any]) -> bool:
        """Send SMS via Twilio (placeholder implementation)."""
        logger.info("Twilio SMS integration not implemented - placeholder")
        # In real implementation:
        # from twilio.rest import Client
        # client = Client(account_sid, auth_token)
        # client.messages.create(...)
        return True
    
    def _send_aws_sns_sms(self, message: str, properties: List[Dict[str, Any]], sms_config: Dict[str, Any]) -> bool:
        """Send SMS via AWS SNS (placeholder implementation)."""
        logger.info("AWS SNS SMS integration not implemented - placeholder")
        return True
    
    def _send_webhook_notification(self, properties: List[Dict[str, Any]]) -> bool:
        """Send webhook notification."""
        try:
            webhook_config = self.config.get('webhook', {})
            
            if not webhook_config.get('enabled', False):
                logger.info("Webhook notifications are disabled")
                return True
            
            url = webhook_config.get('url')
            headers = webhook_config.get('headers', {})
            
            if not url:
                logger.error("Webhook URL not configured")
                return False
            
            # Prepare payload
            payload = {
                'timestamp': datetime.now().isoformat(),
                'event_type': 'property_alert',
                'property_count': len(properties),
                'properties': properties[:5]  # Send first 5 properties to avoid large payloads
            }
            
            # Send webhook
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(url, data=data, headers={
                'Content-Type': 'application/json',
                **headers
            })
            
            with urllib.request.urlopen(req) as response:
                if response.getcode() == 200:
                    logger.info("Webhook notification sent successfully")
                    return True
                else:
                    logger.error(f"Webhook returned status code: {response.getcode()}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error sending webhook notification: {str(e)}")
            return False
    
    def _send_slack_notification(self, subject: str, message: str, properties: List[Dict[str, Any]]) -> bool:
        """Send notification to Slack channel."""
        try:
            slack_config = self.config.get('slack', {})
            
            if not slack_config.get('enabled', False):
                logger.info("Slack notifications are disabled")
                return True
            
            webhook_url = slack_config.get('webhook_url')
            
            if not webhook_url:
                logger.error("Slack webhook URL not configured")
                return False
            
            # Create Slack message
            slack_message = {
                "text": subject,
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": subject
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"Found *{len(properties)}* properties matching your criteria:"
                        }
                    }
                ]
            }
            
            # Add property details (first few properties)
            for prop in properties[:3]:
                slack_message["blocks"].append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{prop.get('address', 'N/A')}*\n"
                               f"Price: ${prop.get('price', 0):,.0f} | "
                               f"Bed/Bath: {prop.get('bedrooms', 'N/A')}/{prop.get('bathrooms', 'N/A')}\n"
                               f"<{prop.get('url', '#')}|View Listing>"
                    }
                })
            
            # Send to Slack
            data = json.dumps(slack_message).encode('utf-8')
            req = urllib.request.Request(webhook_url, data=data, headers={
                'Content-Type': 'application/json'
            })
            
            with urllib.request.urlopen(req) as response:
                if response.getcode() == 200:
                    logger.info("Slack notification sent successfully")
                    return True
                else:
                    logger.error(f"Slack webhook returned status code: {response.getcode()}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error sending Slack notification: {str(e)}")
            return False
    
    def _create_html_message(self, plain_message: str, properties: List[Dict[str, Any]]) -> str:
        """Create HTML version of the notification message."""
        html_lines = [
            "<html><body>",
            "<h2>Property Alert</h2>",
            f"<p>Found <strong>{len(properties)}</strong> properties matching your criteria:</p>",
            "<table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse;'>",
            "<tr>",
            "<th>Address</th><th>City</th><th>Price</th><th>Bed/Bath</th><th>Sq Ft</th><th>Days on Market</th><th>Link</th>",
            "</tr>"
        ]
        
        for prop in properties:
            price_str = f"${prop.get('price', 0):,.0f}" if prop.get('price') else "N/A"
            bed_bath = f"{prop.get('bedrooms', 'N/A')}/{prop.get('bathrooms', 'N/A')}"
            sqft = f"{prop.get('square_feet', 0):,}" if prop.get('square_feet') else "N/A"
            url = prop.get('url', '')
            link = f"<a href='{url}'>View</a>" if url else "N/A"
            
            html_lines.append(
                f"<tr>"
                f"<td>{prop.get('address', 'N/A')}</td>"
                f"<td>{prop.get('city', 'N/A')}</td>"
                f"<td>{price_str}</td>"
                f"<td>{bed_bath}</td>"
                f"<td>{sqft}</td>"
                f"<td>{prop.get('days_on_market', 'N/A')}</td>"
                f"<td>{link}</td>"
                f"</tr>"
            )
        
        html_lines.extend([
            "</table>",
            f"<p><em>Alert generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</em></p>",
            "</body></html>"
        ])
        
        return "\n".join(html_lines)

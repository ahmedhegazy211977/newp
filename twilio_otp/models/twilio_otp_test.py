from odoo import models, fields, api
import logging
from twilio.rest import Client

_logger = logging.getLogger(__name__)

class TwilioOTPTest(models.TransientModel):
    _name = 'twilio.test'
    _description = 'Twilio OTP Test Connection'

    test_phone_number = fields.Char(string="Test Phone Number", required=True)
    test_message = fields.Char(string="Message", readonly=True)

    def action_test_twilio_connection(self):
        """Test the connection to Twilio using the provided phone number."""

        twilio_account_sid = self.env['ir.config_parameter'].sudo().get_param('twilio_otp.twilio_account_sid')
        twilio_auth_token = self.env['ir.config_parameter'].sudo().get_param('twilio_otp.twilio_auth_token')
        twilio_from_number = self.env['ir.config_parameter'].sudo().get_param('twilio_otp.twilio_from_number')

        if not twilio_account_sid or not twilio_auth_token or not twilio_from_number:
            self.test_message = "Twilio credentials are not configured properly."
            return

        try:
            client = Client(twilio_account_sid, twilio_auth_token)
            print(self.test_phone_number)
            print(type(self.test_phone_number))
            message = client.messages.create(
                body="This is a test OTP message from Odoo.",
                from_=f'whatsapp:{twilio_from_number}',
                to=f"whatsapp:{self.test_phone_number}"
            )
            self.test_message = "Test message sent successfully!"
            _logger.info(f"Twilio test message sent, SID: {message.sid}")
        except Exception as e:
            self.test_message = f"Failed to send test message: {str(e)}"
            _logger.error(f"Error while testing Twilio connection: {str(e)}")

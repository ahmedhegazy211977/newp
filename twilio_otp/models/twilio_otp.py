from odoo import models, fields, api
from twilio.rest import Client
from odoo.http import request

class TwilioOTP(models.Model):
    _name = 'twilio.otp'
    _description = 'Twilio OTP Management'

    @api.model
    def send_otp(self, phone_number, country_code):

        account_sid = self.env['ir.config_parameter'].sudo().get_param('twilio_otp.twilio_account_sid')
        auth_token = self.env['ir.config_parameter'].sudo().get_param('twilio_otp.twilio_auth_token')
        from_number = self.env['ir.config_parameter'].sudo().get_param('twilio_otp.twilio_from_number')
        client = Client(account_sid, auth_token)

        if phone_number.startswith('0'):
            phone_number = phone_number[1:]
        otp = self._generate_otp()
        message = client.messages.create(
            from_=f'whatsapp:{from_number}',
            body=f'Your OTP is {otp}',
            to=f"whatsapp:{country_code}{phone_number}"
        )

        request.session['otp_phone_number'] = phone_number
        request.session['otp_country_code'] = country_code
        request.session['otp'] = otp
        return otp

    @api.model
    def resend_otp(self):
        phone_number = request.session.get('otp_phone_number')
        country_code = request.session.get('otp_country_code')
        print(phone_number)
        print(country_code)
        if not phone_number or not country_code:
            return 'Phone number or country code not found in session.'

        account_sid = self.env['ir.config_parameter'].sudo().get_param('twilio_otp.twilio_account_sid')
        auth_token = self.env['ir.config_parameter'].sudo().get_param('twilio_otp.twilio_auth_token')
        from_number = self.env['ir.config_parameter'].sudo().get_param('twilio_otp.twilio_from_number')
        client = Client(account_sid, auth_token)

        otp = self._generate_otp()
        message = client.messages.create(
            from_=f'whatsapp:{from_number}',
            body=f'Your new OTP is {otp}',
            to=f"whatsapp:{country_code}{phone_number}"
        )


        request.session['otp'] = otp

        return otp
    def _generate_otp(self):
        import random
        return random.randint(100000, 999999)

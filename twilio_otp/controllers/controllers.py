from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo import http
from odoo.exceptions import UserError, AccessDenied
from odoo.http import request
import logging
_logger = logging.getLogger(__name__)



class TwilioOTPController(http.Controller):

    @http.route('/web/signup', type='http', auth='public', website=True)
    def web_auth_signup(self, *args, **kw):
        if request.httprequest.method == 'POST':
            phone_number = kw.get('phone')
            country_code = kw.get('country')
            email = kw.get('login')
            password = kw.get('password')
            name = kw.get('name')


            request.session['signup_name'] = name
            request.session['signup_email'] = email
            request.session['signup_password'] = password

            if phone_number:
                otp = request.env['twilio.otp'].send_otp(phone_number,country_code)

                request.session['signup_otp'] = otp

                return request.render('twilio_otp.otp_verification', {})
        return AuthSignupHome().web_auth_signup(*args, **kw)

    @http.route('/web/signup/verify', type='http', auth='public', website=True)
    def web_auth_signup_verify(self, **kw):
        user_otp = kw.get('otp')
        session_otp = request.session.get('signup_otp')


        name = request.session.get('signup_name')
        email = request.session.get('signup_email')
        password = request.session.get('signup_password')
        if not email or not password:
            return request.render('twilio_otp.signup_error', {'error': 'Email and password are required.'})

        _logger.debug(f"Received OTP: {user_otp}, Session OTP: {session_otp}, Email: {email}")

        if user_otp and int(user_otp) == session_otp:
            try:
                user_sudo = request.env['res.users'].sudo()
                existing_user = user_sudo.search([('login', '=', email)], limit=1)

                if existing_user:
                    _logger.warning('User with this email already exists.')
                    return request.render('twilio_otp.signup_error', {'error': 'User with this email already exists.'})

                _logger.info('Creating user...')

                portal_group = request.env.ref('base.group_portal')

                user = user_sudo.create({
                    'name': name,
                    'login': email,
                    'password': password,
                    'groups_id': [(6, 0, [portal_group.id])],
                })

                _logger.info(f'User created successfully: {user.login}')

                return request.redirect('/web/login')

            except Exception as e:
                _logger.error(f'Error during user creation or authentication: {str(e)}')
                return request.render('twilio_otp.signup_error',
                                      {'error': 'An unexpected error occurred. Please try again.'})

        else:
            _logger.warning('Invalid OTP entered by the user.')
            return request.render('twilio_otp.otp_verification', {'error': 'Invalid OTP. Please try again.'})

    @http.route('/web/otp/resend', type='json', auth="public", csrf=False)
    def resend_otp(self):
        session = request.session
        phone_number = session.get('otp_phone_number')
        country_code = session.get('otp_country_code')
        print(phone_number)
        print(country_code)
        if not phone_number or not country_code:
            return {'success': False, 'error': 'Phone number or country code not found in session'}

        otp = request.env['twilio.otp'].sudo().send_otp(phone_number, country_code)
        return {'success': True, 'otp': otp}

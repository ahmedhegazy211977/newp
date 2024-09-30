from random import choice
import string

from odoo.addons.web.controllers.home import Home, ensure_db
from odoo import http, _
from odoo.http import request
from odoo.exceptions import UserError
import requests
MESSAGE_URL = "https://api.oursms.com/msgs/sms"
CREDIT_URL = "https://api.oursms.com/billing/credits"

DEFAULT_ENDPOINT = 'https://iap-sms.odoo.com'
local_endpoint="/"
import logging
_logger = logging.getLogger('OUR-SMS SMS ===>')
from odoo.addons.iap.tools import iap_tools
class OtpSignupHome(Home):

    @http.route(website=True)
    def web_auth_signup(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()
        return super(OtpSignupHome, self).web_auth_signup(*args, **kw)

    @http.route('/web/signup/otp', type='http', auth='public', website=True, sitemap=False)
    def web_signup_otp(self, **kw):
        qcontext = request.params.copy()
        OTP = self.generate_otp(4)
        if "login" in qcontext and qcontext["login"] and qcontext["password"] == qcontext["confirm_password"]:
            user_id = request.env["res.users"].sudo().search([("login", "=", qcontext.get("login"))])
            if user_id:
                qcontext["error"] = _("Another user is already registered using this mobile.")
                response = request.render('sttl_otp_login.custom_otp_signup', qcontext)
                return response
            else:
                mobile = str(qcontext.get('login'))
                name = str(qcontext.get('name'))
                vals = {
                    'otp': OTP,
                    'mobile': mobile
                }
                body = """Dear %s Please use the following One-Time Password (OTP): %s to verify your account""" % (qcontext["name"], OTP)
                self.send_sms(body,mobile)
                response = request.render('sttl_otp_login.custom_otp_signup', {'otp': True, 'otp_login': True,
                                                                               'login': qcontext["login"],
                                                                               'otp_no': OTP,
                                                                               'name': qcontext["name"],
                                                                               'password': qcontext["password"],
                                                                               'confirm_password': qcontext[
                                                                                   "confirm_password"]})
                res = request.env['otp.verification'].sudo().create(vals)
                return response
        else:
            qcontext["error"] = _("Passwords do not match, please retype them.")
            response = request.render('sttl_otp_login.custom_otp_signup', qcontext)
            return response

    @http.route('/web/signup/otp/verify', type='http', auth='public', website=True, sitemap=False)
    def web_otp_signup_verify(self, *args, **kw):
        qcontext = request.params.copy()
        mobile = str(kw.get('login'))
        res_id = request.env['otp.verification'].search([('mobile', '=', mobile)], order="create_date desc", limit=1)
        name = str(kw.get('name'))
        password = str(qcontext.get('password'))
        confirm_password = str(qcontext.get('confirm_password'))

        try:
            otp = str(kw.get('otp'))
            otp_no = res_id.otp
            if otp_no == otp:
                res_id.state = 'verified'
                return self.web_auth_signup(*args, **kw)
            else:
                res_id.state = 'rejected'
                response = request.render('sttl_otp_login.custom_otp_signup', {'otp': True, 'otp_login': True,
                                                                               'login': mobile, 'name': name,
                                                                               'password': password,
                                                                               'confirm_password': confirm_password})
                return response
        except UserError as e:
            qcontext['error'] = e.name or e.value

        response = request.render('sttl_otp_login.custom_otp_signup', {'otp': True, 'otp_login': True,
                                                                       'login': mobile, 'name': name,
                                                                       'password': password,
                                                                       'confirm_password': confirm_password
                                                                       })
        return response

    def generate_otp(self, number_of_digits):
        otp = ''.join(choice(string.digits) for _ in range(number_of_digits))
        return otp
    def send_sms(self,msg,number):
        params={}
        msg_data={}
        account = request.env['iap.account'].sudo().get('sms')
        params['account_token'] = account.account_token
        ICPSudo = request.env['ir.config_parameter'].sudo()
        endpoint = ICPSudo.get_param(
        'sms.endpoint', DEFAULT_ENDPOINT)
        api_sender = request.env.company.oursms_sender
        api_token = request.env.company.oursms_api_token
        if request.env.context.get('sms_sender_id'):
            api_sender = request.env.context.get('sms_sender_id')

        if not (api_token and api_sender):
            raise ValidationError(_('Please Configure OUR-SMS API parameters'))
        msg=msg
        numbers=[number]
        if not numbers:
            raise ValidationError(_('Please Add Mobile Number'))
        sms_state = 'server_error'
        sms_credit = 0
        try:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer %s' % api_token,
            }
            data = {
                "src": api_sender,
                "dests": numbers,
                "body": msg,
                "priority": 0,
                "delay": 0,
                "validity": 0,
                "maxParts": 0,
            }

            response = requests.post(url=MESSAGE_URL, headers=headers, json=data)
            msg_response = response.json()
            _logger.info('Message Response : %s' % msg_response)
            if response.status_code == 200:
                if msg_response.get('accepted') > 0:
                    sms_state = 'success'
            elif response.status_code == 401:
                sms_state = 'server_error'
            credit_response = requests.get(url=CREDIT_URL, headers=headers)
            credit_response = credit_response.json()
            sms_credit = credit_response.get('credits')
            _logger.info('Credit Response : %s' % credit_response)

            msg_data = {'credit': sms_credit, 'state': sms_state}
        except Exception as e:
            _logger.error('Error when sending OUR-SMS: %s' % e)
            res = iap_tools.iap_jsonrpc(endpoint + local_endpoint, params=params, timeout=300)
            return res
        return msg_data

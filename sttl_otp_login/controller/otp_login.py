from random import choice
import string

from odoo.addons.web.controllers.home import Home, ensure_db
from odoo import http, _
from odoo.exceptions import AccessDenied, AccessError, UserError, ValidationError
from odoo.http import request
import requests
MESSAGE_URL = "https://api.oursms.com/msgs/sms"
CREDIT_URL = "https://api.oursms.com/billing/credits"

DEFAULT_ENDPOINT = 'https://iap-sms.odoo.com'
local_endpoint="/"
import logging
_logger = logging.getLogger('OUR-SMS SMS ===>')
from odoo.addons.iap.tools import iap_tools

class OtpLoginHome(Home):
    
    @http.route(website=True)
    def web_login(self, redirect=None, **kw):
        ensure_db()
        providers = {}
        qcontext = request.params.copy()
        qcontext['providers'] = providers

        if request.httprequest.method == 'GET':

            if "otp_login" and "otp" in kw:
                if kw["otp_login"] and kw["otp"]:
                    return request.render("sttl_otp_login.custom_login_template", {'providers':providers,'otp': True, 'otp_login': True})
            if "otp_login" in kw: #checks if the keyword "otp_login" exists in the dict "kw".
                if kw["otp_login"]: #checks if the value of "otp_login" is true.
                    return request.render("sttl_otp_login.custom_login_template", {'providers':providers,'otp_login': True})
            else:
                return super(OtpLoginHome, self).web_login(redirect, **kw)
        else:
            if kw.get('login'):
                request.params['login'] = kw.get('login').strip()
            if kw.get('password'):
                request.params['password'] = kw.get('password').strip()
            return super(OtpLoginHome, self).web_login(redirect, **kw)
        return request.render("sttl_otp_login.custom_login_template", {'providers':providers})

    @http.route('/web/otp/login', type='http', auth='public', website=True, csrf=False)
    def web_otp_login(self, **kw):
        qcontext = request.params.copy()
        mobile = str(qcontext.get('login'))
        user_id = request.env['res.users'].sudo().search([('login', '=', mobile)], limit=1)
        providers = self.list_providers()
        if user_id:
            OTP = self.generate_otp(4)
            vals = {
                'otp': OTP,
                'mobile': mobile
            }
            body = """Dear %s Please use the following One-Time Password (OTP): %s to verify your account""" % (user_id.name, OTP)
            self.send_sms(body,mobile)
            
            response = request.render("sttl_otp_login.custom_login_template", {'otp': True, 'otp_login': True,
                                                                               'login': qcontext["login"],
                                                                               'otp_no': OTP,'providers':providers})
            request.env['otp.verification'].sudo().create(vals)
            return response

        else:
            response = request.render("sttl_otp_login.custom_login_template", {'otp': False, 'otp_login': True,
                                                                               'login_error': True,'providers':providers})
            return response

    @http.route('/web/otp/verify', type='http', auth='public', website=True, csrf=False)
    def web_otp_verify(self, *args, **kw):
        qcontext = request.params.copy()
        mobile = str(kw.get('login'))
        res_id = request.env['otp.verification'].search([('mobile', '=', mobile)], order="create_date desc", limit=1)

        try:
            otp = str(kw.get('otp'))
            otp_no = res_id.otp
            if otp_no == otp:
                res_id.state = 'verified'
                user_id = request.env['res.users'].sudo().search([('login', '=', mobile)], limit=1)
                request.env.cr.execute(
                    "SELECT COALESCE(password, '') FROM res_users WHERE id=%s",
                    [user_id.id]
                )
                hashed = request.env.cr.fetchone()[0]
                qcontext.update({'login': user_id.sudo().login,
                                 'name': user_id.sudo().partner_id.name,
                                 'password': hashed + 'mobile_otp_login'})
                request.params.update(qcontext)
                return self.web_login(*args, **kw)
            else:
                res_id.state = 'rejected'
                response = request.render('sttl_otp_login.custom_login_template', {'otp': True, 'otp_login': True,
                                                                                   'login': mobile})
                return response
        except UserError as e:
            qcontext['error'] = e.name or e.value

        response = request.render('sttl_otp_login.custom_login_template', {'otp': True, 'otp_login': True,
                                                                           'login': mobile})
        return response

    def generate_otp(self, number_of_digits):
        otp = ''.join(choice(string.digits) for _ in range(number_of_digits))
        return otp
    def send_sms(self,msg,number):
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

            msg_data += [{'credit': sms_credit, 'state': sms_state, 'uuid': n[1]}]
        except Exception as e:
            _logger.error('Error when sending OUR-SMS: %s' % e)
            res = iap_tools.iap_jsonrpc(endpoint + local_endpoint, params=params, timeout=300)
            return res
        return msg_data


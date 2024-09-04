# -*- coding: utf-8 -*-

##############################################################################
#    Copyright (C) 2020.
#    Author: Eng.Ramadan Khalil (<rkhalil1990@gmail.com>)
#    website': https://www.linkedin.com/in/ramadan-khalil-a7088164
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
##############################################################################

DEFAULT_ENDPOINT = 'https://iap-sms.odoo.com'
import logging
from odoo.exceptions import ValidationError
import requests
from odoo.addons.iap.tools import iap_tools
from odoo import api, fields, models, _

_logger = logging.getLogger('OUR-SMS SMS ===>')

MESSAGE_URL = "https://api.oursms.com/msgs/sms"
CREDIT_URL = "https://api.oursms.com/billing/credits"
from odoo.addons.sms.tools import sms_api


def _contact_iap(self, local_endpoint, params, timeout=15):
    account = self.env['iap.account'].get('sms')
    params['account_token'] = account.account_token
    ICPSudo = self.env['ir.config_parameter'].sudo()
    endpoint = ICPSudo.get_param(
        'sms.endpoint', DEFAULT_ENDPOINT)
    api_sender = self.env.company.oursms_sender
    api_token = self.env.company.oursms_api_token

    if self.env.context.get('sms_sender_id'):
        api_sender = self.env.context.get('sms_sender_id')

    if not (api_token and api_sender):
        raise ValidationError(_('Please Configure OUR-SMS API parameters'))
    msg_data = []
    messages = params.get('messages', [])
    if not params.get('messages', []) and params.get(
            'numbers') and params.get('message'):
        for number in params.get('numbers'):
            messages.append(
                {'number': number, 'content': params.get('message')})

    for message in messages:
        msg = message.get('content', '')
        numbers_with_uuid = []
        results_uuids = [n['uuid'] for n in message.get('numbers', '')]
        for phone in message.get('numbers', ''):
            number = phone.get('number', '')
            number = number.replace(' ', '').strip().replace('+966', '966')
            numbers_with_uuid.append((number, phone.get('uuid')))
            if not number:
                raise ValidationError(_('Please Add Mobile Number'))
        sms_state = 'server_error'
        sms_credit = 0
        try:

            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer %s' % api_token,
            }
            numbers = [n[0] for n in numbers_with_uuid]
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

            msg_data += [{'credit': sms_credit, 'state': sms_state, 'uuid': n[1],
                          'res_id': message.get('res_id', False)} for n in numbers_with_uuid]


        except Exception as e:
            _logger.error('Error when sending OUR-SMS: %s' % e)
            res = iap_tools.iap_jsonrpc(endpoint + local_endpoint, params=params, timeout=300)
            return res
        return msg_data


sms_api.SmsApi._contact_iap = _contact_iap

# class CDSSmsApi(sms_api.SmsApi):
#
#
#
#     def _contact_iap(self, local_endpoint, params, timeout=15):
#         account = self.env['iap.account'].get('sms')
#         params['account_token'] = account.account_token
#         ICPSudo = self.env['ir.config_parameter'].sudo()
#         endpoint = ICPSudo.get_param(
#             'sms.endpoint', DEFAULT_ENDPOINT)
#         api_sender = self.env.company.oursms_sender
#         api_token = self.env.company.oursms_api_token
#
#         if self.env.context.get('sms_sender_id'):
#             api_sender = self.env.context.get('sms_sender_id')
#
#         if not (api_token and api_sender):
#             raise ValidationError(_('Please Configure OUR-SMS API parameters'))
#         msg_data = []
#         messages = params.get('messages', [])
#         if not params.get('messages', []) and params.get(
#                 'numbers') and params.get('message'):
#             for number in params.get('numbers'):
#                 messages.append(
#                     {'number': number, 'content': params.get('message')})
#
#         for message in messages:
#             msg = message.get('content', '')
#             number = message.get('number', '')
#             number = number.replace(' ', '').strip().replace('+966', '966')
#             if not number:
#                 raise ValidationError(_('Please Add Mobile Number'))
#             sms_state = 'server_error'
#             sms_credit = 0
#             try:
#
#                 headers = {
#                     'Content-Type': 'application/json',
#                     'Authorization': 'Bearer %s' % api_token,
#                 }
#
#                 data = {
#                     "src": api_sender,
#                     "dests": [number],
#                     "body": msg,
#                     "priority": 0,
#                     "delay": 0,
#                     "validity": 0,
#                     "maxParts": 0,
#                 }
#
#                 response = requests.post(url=MESSAGE_URL, headers=headers, json=data)
#                 msg_response = response.json()
#                 _logger.info('Message Response : %s' % msg_response)
#                 if response.status_code == 200:
#                     if msg_response.get('accepted') > 0:
#                         sms_state = 'success'
#                 elif response.status_code == 401:
#                     sms_state = 'server_error'
#                 credit_response = requests.get(url=CREDIT_URL, headers=headers)
#                 credit_response = credit_response.json()
#                 sms_credit = credit_response.get('credits')
#                 _logger.info('Credit Response : %s' % credit_response)
#
#                 msg_data.append({'credit': sms_credit, 'state': sms_state,
#                                  'res_id': message.get('res_id', False)})
#
#
#             except Exception as e:
#                 _logger.error('Error when sending OUR-SMS: %s' % e)
#                 res = iap_tools.iap_jsonrpc(endpoint + local_endpoint, params=params, timeout=300)
#                 return res
#             return msg_data

# sms_api.SmsApi._contact_iap = _contact_iap

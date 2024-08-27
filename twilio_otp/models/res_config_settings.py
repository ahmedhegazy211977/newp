from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    twilio_account_sid = fields.Char(
        string="Twilio Account SID",
        config_parameter='twilio_otp.twilio_account_sid'
    )
    twilio_auth_token = fields.Char(
        string="Twilio Auth Token",
        config_parameter='twilio_otp.twilio_auth_token'
    )
    twilio_from_number = fields.Char(
        string="Twilio From Number",
        config_parameter='twilio_otp.twilio_from_number'
    )

    def set_values(self):
        _logger.info('set_values called')
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('twilio_otp.twilio_account_sid', self.twilio_account_sid)
        self.env['ir.config_parameter'].sudo().set_param('twilio_otp.twilio_auth_token', self.twilio_auth_token)
        self.env['ir.config_parameter'].sudo().set_param('twilio_otp.twilio_from_number', self.twilio_from_number)

    @api.model
    def get_values(self):
        _logger.info('get_values called')
        res = super(ResConfigSettings, self).get_values()
        res.update(
            twilio_account_sid=self.env['ir.config_parameter'].sudo().get_param('twilio_otp.twilio_account_sid'),
            twilio_auth_token=self.env['ir.config_parameter'].sudo().get_param('twilio_otp.twilio_auth_token'),
            twilio_from_number=self.env['ir.config_parameter'].sudo().get_param('twilio_otp.twilio_from_number')

        )
        return res


{
    'name': 'Twilio OTP',
    'version': '1.0',
    'category': 'Authentication',
    'summary': 'Send OTP using Twilio during registration',
    'depends': ['base', 'auth_signup','website'],
    'data': [
       'security/ir.model.access.csv',
       'views/res_config_settings_views.xml',
       'views/otp_verification.xml',
       'views/signup_templates.xml',
       'views/otp_test.xml',

    ],
}

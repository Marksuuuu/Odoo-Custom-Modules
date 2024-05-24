# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import socket
from ast import literal_eval

import requests

from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = ['res.config.settings']

    login_url = fields.Char(string='Url', config_parameter='dex_form_request_approval.login_url')
    sender = fields.Char(string='Sender', config_parameter='dex_form_request_approval.sender')
    host = fields.Char(string='Host', config_parameter='dex_form_request_approval.host')
    port = fields.Integer(string='Port', config_parameter='dex_form_request_approval.port')

    username = fields.Char(string='Username', config_parameter='dex_form_request_approval.username')
    password = fields.Char(string='Password', config_parameter='dex_form_request_approval.password')

    purchase_representative = fields.Many2one('hr.employee', 'Purchase Representative')

    purchase_rep = fields.Many2one('res.users', 'Purchase Representative', config_parameter='dex_form_request_approval.purchase_rep')




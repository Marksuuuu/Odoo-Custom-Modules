# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import socket
from ast import literal_eval

import requests

from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = ['res.config.settings']

    login_url = fields.Char(string='Url', config_parameter='tpc_dm_cm.login_url')
    sender = fields.Char(string='Sender', config_parameter='tpc_dm_cm.sender')
    host = fields.Char(string='Host', config_parameter='tpc_dm_cm.host')
    port = fields.Integer(string='Port', config_parameter='tpc_dm_cm.port')

    username = fields.Char(string='Username', config_parameter='tpc_dm_cm.username')
    password = fields.Char(string='Password', config_parameter='tpc_dm_cm.password')

    file_types = fields.Many2many('file.types', string='File Types')

    connection_bool = fields.Boolean(
        string='Connection Bool',
        compute='_compute_check_ping',
        config_parameter='tpc_dm_cm.connection_bool'
    )

    credentials_bool = fields.Boolean(
        string='Credentials Bool',
        compute='_compute_check_credentials',
        config_parameter='tpc_dm_cm.credentials_bool'
    )

    @api.depends('host', 'port')
    def _compute_check_ping(self):
        for record in self:
            # Check if both 'host' and 'port' have data
            if record.host and record.port:
                # Create a socket object
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)  # Set a timeout for the connection attempt

                try:
                    # Try to connect to the host and port
                    sock.connect((record.host, record.port))
                    record.connection_bool = True
                except socket.error as e:
                    record.connection_bool = False
                finally:
                    # Close the socket
                    sock.close()
            else:
                # Set connection_bool to False if 'host' or 'port' is empty
                record.connection_bool = False

    @api.depends('login_url', 'sender', 'host', 'port', 'username', 'password')
    def _compute_check_credentials(self):
        for record in self:
            # Check if username, password, and login_url have data
            if record.username and record.password and record.login_url:
                # Define the login credentials
                username = record.username
                password = record.password

                # Define the login URL
                login_url = record.login_url  # Replace with the actual login URL

                # Create a session to persist the login session
                session = requests.Session()

                # Prepare the login data
                login_data = {
                    'username': username,
                    'password': password
                }

                try:
                    # Send a POST request to the login URL
                    response = session.post(login_url, data=login_data)
                    response.raise_for_status()  # Raise an HTTPError for bad responses

                    # Check if the login was successful (you may need to adjust this based on the website's response)
                    if "Welcome" in response.text:
                        record.credentials_bool = True
                    else:
                        record.credentials_bool = False
                except requests.exceptions.RequestException as e:
                    # Handle exceptions (e.g., connection error, timeout, etc.)
                    record.credentials_bool = False
            else:
                # Set credentials_bool to False if username, password, or login_url is missing
                record.credentials_bool = False

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('tpc_dm_cm.file_types', self.file_types.ids)
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()

        with_user = self.env['ir.config_parameter'].sudo()
        com_vehicles = with_user.get_param('tpc_dm_cm.file_types')
        res.update(
            file_types=[(6, 0, literal_eval(com_vehicles))] if com_vehicles else False, )
        return res

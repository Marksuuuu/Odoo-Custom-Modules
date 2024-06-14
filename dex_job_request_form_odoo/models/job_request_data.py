from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class JobRequestData(models.Model):
    _name = 'job.request.data'
    _description = 'model for Job Request Form'

    assigned_by = fields.Many2one('res.users', string='Assigned By')
    date = fields.Date(string='Date')
    needed = fields.Date(string='Needed')
    request_assigned = fields.Char(string='Request/Assigned')
    worker = fields.Many2one('res.partner', string='Worker')
    location = fields.Char(string='Location')
    jrf_task = fields.Char(string='JRF/Task')
    date_start = fields.Date(string='Date Start')
    date_done = fields.Date(string='Date Done')
    days_duration = fields.Integer(string='Days Dur.')
    edited_by = fields.Many2one('res.users', string='Edited By')
    edited_date = fields.Datetime(string='Edited Date')

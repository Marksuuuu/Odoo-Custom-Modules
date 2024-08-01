from odoo import models, fields, api
import json


class HistoryLog(models.Model):
    _name = 'history.log'
    _description = 'History Log'

    name = fields.Char(string='Description')
    model = fields.Char(string='Model')
    record_id = fields.Many2one('employee.onboarding.checklist', string='Record ID')
    user_id = fields.Many2one('res.users', string='User')
    change_date = fields.Datetime(string='Change Date', default=fields.Datetime.now)
    changes = fields.Text(string='Changes')
    tracked_record = fields.Reference(
        selection=[('employee.onboarding.checklist', 'Checklist')],
        string='Tracked Record'
    )

    @api.depends('changes')
    def _compute_formatted_changes(self):
        for record in self:
            record.formatted_changes = record.format_changes()

    formatted_changes = fields.Html(string='Formatted Changes', compute='_compute_formatted_changes')

    def format_changes(self):
        try:
            changes = json.loads(self.changes)
            formatted_changes = "<ul>"
            for field, change in changes.items():
                if isinstance(change, dict) and 'old' in change and 'new' in change:
                    formatted_changes += f"<li>{field}: {change['old']} -> {change['new']}</li>"
                else:
                    formatted_changes += f"<li>{field}: {change}</li>"
            formatted_changes += "</ul>"
            return formatted_changes
        except json.JSONDecodeError:
            return self.changes

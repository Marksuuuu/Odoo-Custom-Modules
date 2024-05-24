from odoo import fields, models, api


class SetSchedule(models.Model):
    _name = 'set.schedule'
    _description = 'Set Cron Schedule'

    name = fields.Char(string='Name', required=True)
    model_id = fields.Many2one('ir.model', string='Target Model', required=True, ondelete='restrict')
    field_ids = fields.Many2many('ir.model.fields', string='Fields')
    interval_number = fields.Integer(string='Interval Number')
    interval_type = fields.Selection([
        ('minutes', 'Minutes'),
        ('hours', 'Hours'),
        ('day', 'Day(s)'),
        ('week', 'Week(s)'),
        ('month', 'Month(s)'),
        ('year', 'Year(s)'),
    ], string='Interval Type', default='hours')
    cron_id = fields.Many2one('ir.cron', string='Scheduled Action')

    @api.onchange('model_id')
    def _onchange_model_id(self):
        if self.model_id:
            model_fields = self.env['ir.model.fields'].search([('model', '=', self.model_id.model)])
            self.field_ids = [(6, 0, model_fields.ids)]

    def write(self, vals):
        if 'active' in vals and not vals['active']:
            # Archive instead of deleting
            self.filtered(lambda r: not r.active)._do_archive()
            vals.pop('active')
        return super(SetSchedule, self).write(vals)

    @api.model
    def _do_archive(self):
        self.write({'active': False})

    @api.model
    def _do_something(self, schedule_id):
        # Perform your action here
        schedule_record = self.env['set.schedule'].browse(schedule_id)
        selected_fields = schedule_record.field_ids
        # Example action: print selected fields
        for field in selected_fields:
            if field.ttype == 'many2one' and field.relation == 'res.users':
                print("Field name:", field.name)
                print("Field type:", field.ttype)
                print("Related model:", field.relation)
                print("----------------------------------")

    def to_find(self):
        # Perform your action here
        schedule_record = self.env['set.schedule'].browse(30)
        selected_fields = schedule_record.field_ids
        # Example action: print selected fields
        for field in selected_fields:
            print(field)
            if field.ttype == 'many2one' and field.relation == 'res.users':
                print("Field name:", field.name)
                print("Field type:", field.ttype)
                print("Related model:", field.relation)
                print("----------------------------------")

    def run_scheduled_action(self):
        current_model = self._name
        model_id = self.env['ir.model'].search([('model', '=', current_model)])
        print(model_id.id)
        # # Ensure the model_id exists before proceeding
        # if not self.model_id:
        #     raise ValueError("Model ID is not set")
        #
        # Schedule the action
        cron_interval = fields.Char(string="Cron Interval", default="0 0 * * *")  # Example: Every hour
        interval_number = self.interval_number or 1
        interval_type = self.interval_type
        cron = self.env['ir.cron'].create({
            'name': 'My Scheduled Action',
            'model_id': model_id.id,
            'state': 'code',
            'code': 'model._do_something(%d)' % self.id,
            'interval_number': interval_number,
            'interval_type': interval_type,
            'numbercall': -1,
            'doall': False,
            'active': True,
        })
        self.cron_id = cron.id

    def stop_scheduled_action(self):
        # Deactivate the scheduled action
        if self.cron_id:
            self.cron_id.active = False

from odoo import fields, models, api


class ApproverSetup(models.Model):
    _name = 'approver.setup'
    _description = 'Approver Setup'
    _rec_name = 'dept_name'

    dept_name = fields.Many2one('hr.department', required=True)
    approval_type = fields.Selection([
        ('official_business', 'Official Business Form'),
        ('it_request', 'IT Request Form'),
        ('overtime_authorization', 'Overtime Authorization'),
        ('gasoline_allowance', 'Gasoline Allowance'),
        ('online_purchases', 'Online Purchases'),
        ('cash_advance', 'Request for Cash Advance'),
        ('grab_request', 'Grab Request Form'),
        ('client_pickup', 'Client Pickup Permit'),
        ('payment_request', 'Payment Request'),
        ('job_request', 'Job Request'),
        ('onboarding_checklist', 'Onboarding Request Form'),
        ('transport_network_vehicle', 'Transport Network Vehicle'),
    ], string='Form Types', required=True)
    no_of_approvers = fields.Integer()
    set_first_approvers = fields.One2many('approver.setup.lines', 'first_approvers_id')
    set_second_approvers = fields.One2many('approver.setup.lines', 'second_approvers_id')
    set_third_approvers = fields.One2many('approver.setup.lines', 'third_approvers_id')
    set_fourth_approvers = fields.One2many('approver.setup.lines', 'fourth_approvers_id')
    set_fifth_approvers = fields.One2many('approver.setup.lines', 'fifth_approvers_id')

    is_need_request_handlers = fields.Boolean(default=False)

    is_need_to_billed = fields.Boolean(string='Required Bill?', default=False)


    requests_handlers = fields.Many2many('res.users')


class ApproverSetupLines(models.Model):
    _name = 'approver.setup.lines'
    _description = 'Form Types Lines'

    first_approvers_id = fields.Many2one('approver.setup')
    second_approvers_id = fields.Many2one('approver.setup')
    third_approvers_id = fields.Many2one('approver.setup')
    fourth_approvers_id = fields.Many2one('approver.setup')
    fifth_approvers_id = fields.Many2one('approver.setup')

    first_approver = fields.Many2one('hr.employee')
    second_approver = fields.Many2one('hr.employee')
    third_approver = fields.Many2one('hr.employee')
    fourth_approver = fields.Many2one('hr.employee')
    fifth_approver = fields.Many2one('hr.employee')
    approver_email = fields.Char(string="Email")
    type = fields.Selection([
        ('first', 'First Approver'),
        ('second', 'Second Approver'),
        ('third', 'Third Approver'),
        ('fourth', 'Fourth Approver'),
        ('fifth', 'Fifth Approver')])

    @api.onchange('first_approver', 'second_approver', 'third_approver', 'fourth_approver', 'fifth_approver', )
    def get_approver_email(self):
        for rec in self:
            if rec.first_approver:
                rec.approver_email = rec.first_approver.work_email
                rec.type = 'first'
            if rec.second_approver:
                rec.approver_email = rec.second_approver.work_email
                rec.type = 'second'
            if rec.third_approver:
                rec.approver_email = rec.third_approver.work_email
                rec.type = 'third'
            if rec.fourth_approver:
                rec.approver_email = rec.fourth_approver.work_email
                rec.type = 'fourth'
            if rec.fifth_approver:
                rec.approver_email = rec.fifth_approver.work_email
                rec.type = 'fifth'

from odoo import fields, models, api, _



class DepartmentApprovers(models.Model):
    _name = "department.approvers"

    dept_name = fields.Many2one('account.analytic.account')
    approval_type = fields.Many2one('purchase.approval.types')
    no_of_approvers = fields.Integer()
    set_first_approvers = fields.One2many('department.approvers.line', 'first_approvers_id')
    set_second_approvers = fields.One2many('department.approvers.line', 'second_approvers_id')
    set_third_approvers = fields.One2many('department.approvers.line', 'third_approvers_id')
    set_fourth_approvers = fields.One2many('department.approvers.line', 'fourth_approvers_id')
    set_fifth_approvers = fields.One2many('department.approvers.line', 'fifth_approvers_id')



class DepartmentApproversLine(models.Model):
    _name = "department.approvers.line"

    first_approvers_id = fields.Many2one('department.approvers')
    second_approvers_id = fields.Many2one('department.approvers')
    third_approvers_id = fields.Many2one('department.approvers')
    fourth_approvers_id = fields.Many2one('department.approvers')
    fifth_approvers_id = fields.Many2one('department.approvers')

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



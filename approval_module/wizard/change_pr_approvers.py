# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ChangePRApprovers(models.TransientModel):
    _name = 'change.pr.approvers'

    approver_id = fields.Many2one('hr.employee', string="Approver", domain=lambda self: self.get_approver_domain())
    department_id = fields.Many2one('account.analytic.account', string="Department", store=True)
    reason = fields.Many2one('change.approver.rsn', string="Reason for Change")
    date = fields.Date(string="Date of Change",
                       default=lambda self: self._context.get('date', fields.Date.context_today(self)))

    @api.onchange('department_id')
    def get_approver_domain(self):
        active_id = self._context.get('active_id')
        purchase_id = self.env['purchase.requisition'].browse(active_id)
        for rec in purchase_id:
            domain = []
            res = self.env["department.approvers"].search(
                [("dept_name", "=", rec.department_id.id), ("approval_type.name", '=', 'Purchase Orders')])

            if rec.department_id and rec.approval_stage == 1:
                approver_dept = [x.first_approver.id for x in res.set_first_approvers]
                rec.approver_id = approver_dept[0]
                domain.append(('id', '=', approver_dept))

            elif rec.department_id and rec.approval_stage == 2:
                approver_dept = [x.second_approver.id for x in res.set_second_approvers]
                rec.approver_id = approver_dept[0]
                domain.append(('id', '=', approver_dept))

            elif rec.department_id and rec.approval_stage == 3:
                approver_dept = [x.third_approver.id for x in res.set_third_approvers]
                rec.approver_id = approver_dept[0]
                domain.append(('id', '=', approver_dept))

            elif rec.department_id and rec.approval_stage == 4:
                approver_dept = [x.fourth_approver.id for x in res.set_fourth_approvers]
                rec.approver_id = approver_dept[0]
                domain.append(('id', '=', approver_dept))

            elif rec.department_id and rec.approval_stage == 5:
                approver_dept = [x.fifth_approver.id for x in res.set_fifth_approvers]
                rec.approver_id = approver_dept[0]
                domain.append(('id', '=', approver_dept))

            else:
                domain = []

            return {'domain': {'approver_id': domain}}

    def button_submit(self):
        active_id = self._context.get('active_id')
        purchase_id = self.env['purchase.requisition'].browse(active_id)
        approval_type = self.env["purchase.approval.types"].search([("name", '=', 'Purchase Requests')])
        vals = {
            'approver_id': self.approver_id.id,

        }

        purchase_id.write(vals)

        history = self.env['change.approver.rsn'].create({
            'name': self.reason.name,
            'approval_type': approval_type.id,
            'date': self.date
        })

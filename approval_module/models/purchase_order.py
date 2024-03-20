from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    approver_id = fields.Many2one('hr.employee', string="Approver", domain=lambda self: self.get_approver_domain())
    approval_stage = fields.Integer(default=1)
    department_id = fields.Many2one('account.analytic.account', string="Department", store=True)
    to_approve = fields.Boolean()
    to_approve_po = fields.Boolean()
    show_submit_request = fields.Boolean()
    date_request = fields.Datetime(string="Request Date", compute="_compute_date")
    date_request_deadline = fields.Date(string="Request Deadline", compute="_compute_date")
    state = fields.Selection(
        selection_add=[('to_approve', 'To Approve'), ('disapprove', 'Disapproved'), ('approved', 'Approved')])
    approval_status = fields.Selection(selection=[
        ('po_approval', 'For Approval'),
        ('approved', 'Approved'),
        ('disapprove', 'Disapproved'),
        ('cancel', 'Cancelled')
    ], string='Status')

    disapproval_reason = fields.Char(string="Reason for Disapproval")
    show_request = fields.Char()
    approval_type_id = fields.Many2one('purchase.approval.types')
    approval_id = fields.Many2one('purchase.approval')
    is_approver = fields.Boolean(compute="compute_approver")

    # def _compute_approver(self):
    #     for rec in self:
    #         if self.env.user == rec.approver_id.user_id:
    #             self.update({
    #                 'is_approver': True,
    #
    #             })
    #         else:
    #             self.update({
    #                 'is_approver': False,
    #             })

    def compute_approver(self):
        for rec in self:
            if self.env.user.name == rec.approver_id.name:
                self.update({
                    'is_approver': True,
                })
            else:
                self.update({
                    'is_approver': False,
                })

    def submit_for_approval(self):
        self.write({
            'approval_status': 'po_approval',
            'state': 'to_approve',
            'to_approve': True,
            'show_submit_request': False
        })

    def _compute_date(self):
        for rec in self:
            rec.date_request = rec.requisition_id.ordering_date
            rec.date_request_deadline = rec.requisition_id.date_end

    @api.onchange('department_id', 'approval_stage')
    def get_approver_domain(self):
        for rec in self:
            domain = []

            res = self.env["department.approvers"].search(
                [("dept_name", "=", rec.department_id.id), ("approval_type.name", '=', 'Purchase Orders')])

            if rec.department_id and rec.approval_stage == 1:
                try:
                    approver_dept = [x.first_approver.id for x in res.set_first_approvers]
                    rec.approver_id = approver_dept[0]
                    domain.append(('id', '=', approver_dept))

                except IndexError:
                    raise UserError(_("No Approvers set for {}!").format(rec.department_id.name))

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

    @api.depends('approval_stage')
    def approve_request(self):
        for rec in self:
            res = self.env["department.approvers"].search(
                [("dept_name", "=", rec.department_id.id), ("approval_type.name", '=', 'Purchase Orders')])
            if rec.approver_id and rec.approval_stage < res.no_of_approvers:
                if rec.approval_stage == 1:
                    approver_dept = [x.second_approver.id for x in res.set_second_approvers]
                    self.write({
                        'approver_id': approver_dept[0]
                    })

                if rec.approval_stage == 2:
                    approver_dept = [x.third_approver.id for x in res.set_third_approvers]
                    self.write({
                        'approver_id': approver_dept[0]
                    })
                if rec.approval_stage == 3:
                    approver_dept = [x.fourth_approver.id for x in res.set_fourth_approvers]
                    self.write({
                        'approver_id': approver_dept[0]
                    })
                if rec.approval_stage == 4:
                    approver_dept = [x.fifth_approver.id for x in res.set_fifth_approvers]
                    self.write({
                        'approver_id': approver_dept[0]
                    })
                rec.approval_stage += 1
            else:
                self.write({
                    'state': 'approved',
                    'approval_status': 'approved'
                })

    def button_cancel(self):
        for order in self:
            for inv in order.invoice_ids:
                if inv and inv.state not in ('cancel', 'draft'):
                    raise UserError(
                        _("Unable to cancel this purchase order. You must first cancel the related vendor bills."))

        self.write({'state': 'cancel',
                    'approval_status': 'cancel'})

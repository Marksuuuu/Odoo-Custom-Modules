from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = "purchase.requisition"

    approver_id = fields.Many2one('hr.employee', string="Approver", domain=lambda self: self.get_approver_domain())
    approval_stage = fields.Integer(default=1)
    department_id = fields.Many2one('account.analytic.account', string="Department", store=True)
    to_approve = fields.Boolean()
    to_approve_po = fields.Boolean()
    show_submit_request = fields.Boolean()
    state = fields.Selection(
        selection_add=[('to_approve', 'To Approve'), ('open',), ('approved', 'Approved'), ('disapprove', 'Disapproved')])
    state_blanket_order = fields.Selection(
        selection_add=[('to_approve', 'To Approve'), ('open',), ('approved', 'Approved'), ('disapprove', 'Disapproved')])
    approval_status = fields.Selection(selection=[
        ('pr_approval', 'For Approval'),
        ('approved', 'Approved'),
        ('disapprove', 'Disapproved'),
        ('cancel', 'Cancelled')
    ], string='Status')

    disapproval_reason = fields.Char(string="Reason for Disapproval")
    show_request = fields.Char()
    approval_type_id = fields.Many2one('purchase.approval.types')
    approval_id = fields.Many2one('purchase.approval')
    is_approver = fields.Boolean(compute="compute_approver")

    def action_in_progress(self):
        self.ensure_one()
        if not all(obj.line_ids for obj in self):
            raise UserError(_("You cannot confirm agreement {} because there is no product line.").format(self.name))
        if self.type_id.quantity_copy == 'none' and self.vendor_id:
            for requisition_line in self.line_ids:
                if requisition_line.price_unit <= 0.0:
                    raise UserError(_('You cannot confirm the blanket order without price.'))
                if requisition_line.product_qty <= 0.0:
                    raise UserError(_('You cannot confirm the blanket order without quantity.'))
                requisition_line.create_supplier_info()
            self.write({'state': 'to_approve'})
        else:
            self.write({'state': 'to_approve'})
        # Set the sequence number regarding the requisition type
        if self.name == 'New':
            if self.is_quantity_copy != 'none':
                self.name = self.env['ir.sequence'].next_by_code('purchase.requisition.purchase.tender')
            else:
                self.name = self.env['ir.sequence'].next_by_code('purchase.requisition.blanket.order')

        self.write({
            'show_submit_request': True
        })

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
                print('true')
                self.update({
                    'is_approver': True,
                })
            else:
                self.update({
                    'is_approver': False,
                })

    def submit_for_approval(self):
        for rec in self:
            self.write({
                'approval_status': 'pr_approval',
                'to_approve': True,
                'show_submit_request': False
            })

    @api.onchange('department_id', 'approval_stage')
    def get_approver_domain(self):
        for rec in self:
            domain = []
            res = self.env["department.approvers"].search(
                [("dept_name", "=", rec.department_id.id), ("approval_type.name", '=', 'Purchase Requests')])

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
                [("dept_name", "=", rec.department_id.id), ("approval_type.name", '=', 'Purchase Requests')])
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

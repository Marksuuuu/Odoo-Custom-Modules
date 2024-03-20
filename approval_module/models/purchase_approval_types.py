from ast import literal_eval

from odoo import fields, models, api, _


class PurchaseApprovalTypes(models.Model):
    _name = "purchase.approval.types"

    def _default_analytic_account(self):
        analytic_obj = self.env['account.analytic.account'].search([])
        analytic_rec = [{'departments': rec, 'no_approvers': 1, 'dept_code': rec.code} for rec in analytic_obj]
        res = [(0, 0, rec) for rec in analytic_rec]
        return res

    name = fields.Char(string='Type')
    approver_line_ids = fields.One2many('purchase.approval.types.line', 'approver_dept_id',
                                        default=_default_analytic_account)
    set_line_ids = fields.One2many(related='approver_line_ids')
    purchase_request_count = fields.Integer(compute='_compute_count')
    purchase_order_count = fields.Integer(compute='_compute_count')
    image = fields.Binary()

    def _compute_count(self):
        for rec in self:
            rec.purchase_request_count = self.env['purchase.requisition'].search_count(
                [('approval_status', '=', 'pr_approval')])
            rec.purchase_order_count = self.env['purchase.order'].search_count(
                [('approval_status', '=', 'po_approval')])

    def view_purchase(self):
        for rec in self:
            if rec.name == 'Purchase Requests':
                action = self.env.ref('approval_module.purchase_request_to_approve').read()[0]
            else:
                action = self.env.ref('approval_module.view_purchase_order').read()[0]
            return action

    def get_action_purchase_order(self):
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'purchase.order',
            'view_id': self.env.ref('purchase.purchase_order_form').id,
        }

    def get_action_purchase_request(self):
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'purchase.requisition',
            'view_id': self.env.ref('purchase_requisition.view_purchase_requisition_form').id,
        }

    def view_purchase_for_review(self):
        for rec in self:
            if rec.name == 'Purchase Requests':
                action = self.env.ref('approval_module.purchase_request_to_approve').read()[0]
                action['domain'] = [('approval_status', '=', 'pr_approval')]
            else:
                action = self.env.ref('approval_module.view_purchase_order').read()[0]
                action['domain'] = [('approval_status', '=', 'po_approval')]
            return action


class PurchaseApprovaTypesLine(models.Model):
    _name = "purchase.approval.types.line"

    approver_dept_id = fields.Many2one('purchase.approval.types')
    departments = fields.Many2one('account.analytic.account')
    no_approvers = fields.Integer(string="Minimum Approvers")
    dept_code = fields.Char()
    set_approvers = fields.Many2one('hr.employee')
    # view_approvers = fields.Many2many('department.approvers.line', compute='_compute_approver_ids')
    view_first_approvers = fields.Many2many('department.approvers.line', compute='_compute_approver_ids')
    view_second_approvers = fields.Many2many('department.approvers.line', compute='_compute_approver_ids')
    view_third_approvers = fields.Many2many('department.approvers.line', compute='_compute_approver_ids')
    view_fourth_approvers = fields.Many2many('department.approvers.line', compute='_compute_approver_ids')
    view_fifth_approvers = fields.Many2many('department.approvers.line', compute='_compute_approver_ids')
    dept_approvers = fields.Many2one('department.approvers')

    def view_department_approvers(self):

        dept_approvers = self.env['department.approvers'].search(
            [('approval_type', '=', self.approver_dept_id.id), ('dept_name', '=', self.departments.id)])

        if dept_approvers:
            return {
                'res_model': 'department.approvers',
                'res_id': dept_approvers.id,
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'view_id': self.env.ref('approval_module.view_set_approvers_form').id,
            }
        else:
            return {
                'res_model': 'department.approvers',
                # 'dept_name': "self.departments.id",
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'view_id': self.env.ref('approval_module.view_set_approvers_form').id,
                'context': {'default_dept_name': self.departments.id,
                            'default_no_of_approvers': self.no_approvers,
                            'default_approval_type': self.approver_dept_id.id}
            }

    @api.depends('departments')
    def _compute_approver_ids(self):
        for rec in self:
            dept_approvers = self.env['department.approvers'].search([('dept_name', '=', rec.departments.id)])

            # rec.view_approvers = dept_approvers.set_first_approvers
            rec.view_first_approvers = dept_approvers.set_first_approvers
            rec.view_second_approvers = dept_approvers.set_second_approvers
            rec.view_third_approvers = dept_approvers.set_third_approvers
            rec.view_fourth_approvers = dept_approvers.set_fourth_approvers
            rec.view_fifth_approvers = dept_approvers.set_fifth_approvers

# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class TpcDmCm(models.Model):
    _name = 'tpc.dm.cm'
    _description = 'Team Pacific Corporation DM CM Module'

    state = fields.Char(string='Type')
    tpc_dm_cm_line_ids = fields.One2many('tpc.dm.cm.line', 'tpc_dm_cm_id')
    set_line_ids = fields.One2many(related='tpc_dm_cm_line_ids')
    total_count = fields.Integer()
    image = fields.Binary()

    def count(self):
        pass

    def get_names(self):
        pass

    @api.model
    def kanban_data(self):
        to_approve = self._get_state_and_update('to_approve')
        cancel = self._get_state_and_update('cancel')
        disapprove = self._get_state_and_update('disapprove')
        approve = self._get_state_and_update('approved')
        billed = self._get_state_and_update('billed')
        paid = self._get_state_and_update('paid')

        total_to_approve_count = self._get_total_count('to_approve')
        cancel_count = self._get_total_count('cancel')
        disapprove_count = self._get_total_count('disapprove')
        total_approved_count = self._get_total_count('approved')
        total_billed_count = self._get_total_count('billed')
        total_paid_count = self._get_total_count('paid')

        self._update_record(to_approve, total_to_approve_count, 'to_approve')
        self._update_record(cancel, cancel_count, 'cancel')
        self._update_record(disapprove, disapprove_count, 'disapprove')
        self._update_record(approve, total_approved_count, 'approved')
        self._update_record(billed, total_billed_count, 'billed')
        self._update_record(paid, total_paid_count, 'paid')

    def _get_state_and_update(self, state):
        request = self.env['tpc.dm.cm.request'].search([('state', '=', state)], limit=1)

        if request:
            cm_record = self.env['tpc.dm.cm'].search([('state', '=', state)], limit=1)

            if not cm_record:
                self.env['tpc.dm.cm'].create({'state': request.state})

            return request.state
        else:
            return False

    def _get_total_count(self, state):
        return self.env['tpc.dm.cm.request'].search_count([('state', '=', state)])

    def _update_record(self, state, total_count, label):
        if state:
            cm_record = self.env['tpc.dm.cm'].search([('state', '=', state)], limit=1)
            if cm_record:
                cm_record.write({'total_count': total_count})
            else:
                cm_record.write({'total_count': total_count})
        else:
            write_zero = self.env['tpc.dm.cm'].search([('state', '=', label)], limit=1)
            write_zero.write({'total_count': total_count})

    def billing_request(self):
        for rec in self:
            if rec.state == 'to_approve':
                action = self.env.ref('tpc_dm_cm.tpc_dm_cm_request_act_window').read()[0]
            else:
                action = self.env.ref('tpc_dm_cm.tpc_dm_cm_request_act_window').read()[0]
            return action

    def view_for_review(self):
        for rec in self:
            if rec.state == 'to_approve':
                action = self.env.ref('tpc_dm_cm.tpc_dm_cm_request_act_window').read()[0]
                action['domain'] = [('approval_status', '=', 'pr_approval')]
            elif rec.state == 'cancel':
                action = self.env.ref('tpc_dm_cm.tpc_dm_cm_request_act_window').read()[0]
                action['domain'] = [('approval_status', '=', 'cancel')]
            elif rec.state == 'disapprove':
                action = self.env.ref('tpc_dm_cm.tpc_dm_cm_request_act_window').read()[0]
                action['domain'] = [('approval_status', '=', 'disapprove')]
            elif rec.state == 'approved':
                action = self.env.ref('tpc_dm_cm.tpc_dm_cm_request_act_window').read()[0]
                action['domain'] = [('approval_status', '=', 'approved')]
            elif rec.state == 'billed':
                action = self.env.ref('tpc_dm_cm.tpc_dm_cm_request_act_window').read()[0]
                action['domain'] = [('approval_status', '=', 'billed')]
            else:
                action = self.env.ref('tpc_dm_cm.tpc_dm_cm_request_act_window').read()[0]
                action['domain'] = [('approval_status', '=', 'paid')]
            return action

    def get_action_request(self):
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'tpc.dm.cm.request',
            'view_id': self.env.ref('tpc_dm_cm.tpc_dm_cm_request_form_view').id,
        }


class TpcDmCmLine(models.Model):
    _name = "tpc.dm.cm.line"

    tpc_dm_cm_id = fields.Many2one('tpc.dm.cm')
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
            [('approval_type', '=', self.tpc_dm_cm_id.id), ('dept_name', '=', self.departments.id)])

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
                            'default_approval_type': self.tpc_dm_cm_id.id}
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

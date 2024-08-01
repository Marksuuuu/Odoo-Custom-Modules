from odoo import fields, models, api
import re


class PreviewDashboard(models.Model):
    _name = 'preview.dashboard'
    _description = 'Dashboard Preview'

    name = fields.Char('Name')
    model_name = fields.Char('Model Name')
    total_count_to_approve = fields.Integer(string="To Approve")
    total_count_disapprove = fields.Integer(string="Disapprove")
    total_count_approved = fields.Integer(string="Approved")
    total_count_draft = fields.Integer(string="Draft")
    total_count_cancel = fields.Integer(string="Cancelled")

    preview_dashboard_conn = fields.One2many('preview.dashboard.lines', 'preview_dashboard_ids')

    @api.model
    def kanban_data(self):
        models_data = {
            'client.pick.up.permit': {
                'to_approve': 'total_count_to_approve',
                'disapprove': 'total_count_disapprove',
                'approved': 'total_count_approved',
                'draft': 'total_count_draft',
                'cancel': 'total_count_cancel',
            },
            'gasoline.allowance.form': {
                'to_approve': 'total_count_to_approve',
                'disapprove': 'total_count_disapprove',
                'approved': 'total_count_approved',
                'draft': 'total_count_draft',
                'cancel': 'total_count_cancel',
            },
            'grab.request.form': {
                'to_approve': 'total_count_to_approve',
                'disapprove': 'total_count_disapprove',
                'approved': 'total_count_approved',
                'draft': 'total_count_draft',
                'cancel': 'total_count_cancel',
            },
            # 'official.business.form': {
            #     'to_approve': 'total_count_to_approve',
            #     'disapprove': 'total_count_disapprove',
            #     'approved': 'total_count_approved',
            #     'draft': 'total_count_draft',
            #     'cancel': 'total_count_cancel',
            # },
            'on.line.purchases': {
                'to_approve': 'total_count_to_approve',
                'disapprove': 'total_count_disapprove',
                'approved': 'total_count_approved',
                'draft': 'total_count_draft',
                'cancel': 'total_count_cancel',
            },
            # 'overtime.authorization.form': {
            #     'to_approve': 'total_count_to_approve',
            #     'disapprove': 'total_count_disapprove',
            #     'approved': 'total_count_approved',
            #     'draft': 'total_count_draft',
            #     'cancel': 'total_count_cancel',
            # },
            'request.for.cash.advance': {
                'to_approve': 'total_count_to_approve',
                'disapprove': 'total_count_disapprove',
                'approved': 'total_count_approved',
                'draft': 'total_count_draft',
                'cancel': 'total_count_cancel',
            },
            'it.request.form': {
                'to_approve': 'total_count_to_approve',
                'disapprove': 'total_count_disapprove',
                'approved': 'total_count_approved',
                'draft': 'total_count_draft',
                'cancel': 'total_count_cancel',
            },
            'transport.network.vehicle.form': {
                'to_approve': 'total_count_to_approve',
                'disapprove': 'total_count_disapprove',
                'approved': 'total_count_approved',
                'draft': 'total_count_draft',
                'cancel': 'total_count_cancel',
            },
            'payment.request.form': {
                'to_approve': 'total_count_to_approve',
                'disapprove': 'total_count_disapprove',
                'approved': 'total_count_approved',
                'draft': 'total_count_draft',
                'cancel': 'total_count_cancel',
            },
            # Add other models here
        }

        for model_name, fields_map in models_data.items():
            for state, field_name in fields_map.items():
                total_count = self._get_total_count(model_name, state)
                self._update_record(field_name, total_count, model_name)

    def _get_total_count(self, model_name, state):
        try:
            return self.env[model_name].search_count([('state', '=', state)])
        except Exception as e:
            # Handle exception gracefully, log it or print it
            print(f"Error while fetching count for {state} in {model_name}: {e}")
            return 0

    def to_approve(self):
        if self.model_name == 'Client Pick Up Permit':
            action = self.env.ref('dex_form_request_approval.client_pickup_permit_form_action_id').read()[0]
            action['domain'] = [('state', '=', 'to_approve')]
        elif self.model_name == 'Gasoline Allowance Form':
            action = self.env.ref('dex_form_request_approval.gasoline_allowance_form_action_id').read()[0]
            action['domain'] = [('state', '=', 'to_approve')]
        elif self.model_name == 'Grab Request Form':
            action = self.env.ref('dex_form_request_approval.grab_request_form_form_action_id').read()[0]
            action['domain'] = [('state', '=', 'to_approve')]
        # elif self.model_name == 'Official Business Form':
        #     action = self.env.ref('dex_form_request_approval.official_business_form_action_id').read()[0]
        #     action['domain'] = [('state', '=', 'to_approve')]
        elif self.model_name == 'On Line Purchases':
            action = self.env.ref('dex_form_request_approval.online_purchases_form_action_id').read()[0]
            action['domain'] = [('state', '=', 'to_approve')]
        # elif self.model_name == 'Overtime Authorization Form':
        #     action = self.env.ref('dex_form_request_approval.overtime_authorization_form_action_id').read()[0]
        #     action['domain'] = [('state', '=', 'to_approve')]
        elif self.model_name == 'Request For Cash Advance':
            action = self.env.ref('dex_form_request_approval.request_for_cash_advance_form_action_id').read()[0]
            action['domain'] = [('state', '=', 'to_approve')]
        elif self.model_name == 'It Request Form':
            action = self.env.ref('dex_form_request_approval.it_request_form_action_id').read()[0]
            action['domain'] = [('state', '=', 'to_approve')]
        elif self.model_name == 'Transport Network Vehicle Form':
            action = self.env.ref('dex_form_request_approval.transport_network_vehicle_form_action_id').read()[0]
            action['domain'] = [('state', '=', 'to_approve')]
        elif self.model_name == 'Payment Request Form':
            action = self.env.ref('dex_form_request_approval.payment_request_form_action_id').read()[0]
            action['domain'] = [('state', '=', 'to_approve')]
        else:
            action = self.env.ref('dex_form_request_approval.view_preview_dashboard_kanban').read()[0]
        return action

    def cancelled(self):
        if self.model_name == 'Client Pick Up Permit':
            action = self.env.ref('dex_form_request_approval.client_pickup_permit_form_action_id').read()[0]
            action['domain'] = [('state', '=', 'cancel')]
        elif self.model_name == 'Gasoline Allowance Form':
            action = self.env.ref('dex_form_request_approval.gasoline_allowance_form_action_id').read()[0]
            action['domain'] = [('state', '=', 'cancel')]
        elif self.model_name == 'Grab Request Form':
            action = self.env.ref('dex_form_request_approval.grab_request_form_form_action_id').read()[0]
            action['domain'] = [('state', '=', 'cancel')]
        #         elif self.model_name == 'Official Business Form':
        #             action = self.env.ref('dex_form_request_approval.official_business_form_action_id').read()[0]
        #             action['domain'] = [('state', '=', 'cancel')]
        elif self.model_name == 'On Line Purchases':
            action = self.env.ref('dex_form_request_approval.online_purchases_form_action_id').read()[0]
            action['domain'] = [('state', '=', 'cancel')]
        #         elif self.model_name == 'Overtime Authorization Form':
        #             action = self.env.ref('dex_form_request_approval.overtime_authorization_form_action_id').read()[0]
        #             action['domain'] = [('state', '=', 'cancel')]
        elif self.model_name == 'Request For Cash Advance':
            action = self.env.ref('dex_form_request_approval.request_for_cash_advance_form_action_id').read()[0]
            action['domain'] = [('state', '=', 'cancel')]
        elif self.model_name == 'It Request Form':
            action = self.env.ref('dex_form_request_approval.it_request_form_action_id').read()[0]
            action['domain'] = [('state', '=', 'cancel')]
        elif self.model_name == 'Transport Network Vehicle Form':
            action = self.env.ref('dex_form_request_approval.transport_network_vehicle_form_action_id').read()[0]
            action['domain'] = [('state', '=', 'cancel')]
        elif self.model_name == 'Payment Request Form':
            action = self.env.ref('dex_form_request_approval.payment_request_form_action_id').read()[0]
            action['domain'] = [('state', '=', 'cancel')]
        else:
            action = self.env.ref('dex_form_request_approval.view_preview_dashboard_kanban').read()[0]
        return action

    def disapproved(self):
        if self.model_name == 'Client Pick Up Permit':
            action = self.env.ref('dex_form_request_approval.client_pickup_permit_form_action_id').read()[0]
            action['domain'] = [('state', '=', 'disapprove')]
        elif self.model_name == 'Gasoline Allowance Form':
            action = self.env.ref('dex_form_request_approval.gasoline_allowance_form_action_id').read()[0]
            action['domain'] = [('state', '=', 'disapprove')]
        elif self.model_name == 'Grab Request Form':
            action = self.env.ref('dex_form_request_approval.grab_request_form_form_action_id').read()[0]
            action['domain'] = [('state', '=', 'disapprove')]
        #         elif self.model_name == 'Official Business Form':
        #             action = self.env.ref('dex_form_request_approval.official_business_form_action_id').read()[0]
        #             action['domain'] = [('state', '=', 'disapprove')]
        elif self.model_name == 'On Line Purchases':
            action = self.env.ref('dex_form_request_approval.online_purchases_form_action_id').read()[0]
            action['domain'] = [('state', '=', 'disapprove')]
        #         elif self.model_name == 'Overtime Authorization Form':
        #             action = self.env.ref('dex_form_request_approval.overtime_authorization_form_action_id').read()[0]
        #             action['domain'] = [('state', '=', 'disapprove')]
        elif self.model_name == 'Request For Cash Advance':
            action = self.env.ref('dex_form_request_approval.request_for_cash_advance_form_action_id').read()[0]
            action['domain'] = [('state', '=', 'disapprove')]
        elif self.model_name == 'It Request Form':
            action = self.env.ref('dex_form_request_approval.it_request_form_action_id').read()[0]
            action['domain'] = [('state', '=', 'disapprove')]
        elif self.model_name == 'Transport Network Vehicle Form':
            action = self.env.ref('dex_form_request_approval.transport_network_vehicle_form_action_id').read()[0]
            action['domain'] = [('state', '=', 'disapprove')]
        elif self.model_name == 'Payment Request Form':
            action = self.env.ref('dex_form_request_approval.payment_request_form_action_id').read()[0]
            action['domain'] = [('state', '=', 'disapprove')]
        else:
            action = self.env.ref('dex_form_request_approval.view_preview_dashboard_kanban').read()[0]
        return action

    def approved(self):
        if self.model_name == 'Client Pick Up Permit':
            action = self.env.ref('dex_form_request_approval.client_pickup_permit_form_action_id').read()[0]
            action['domain'] = [('state', '=', 'approved')]
        elif self.model_name == 'Gasoline Allowance Form':
            action = self.env.ref('dex_form_request_approval.gasoline_allowance_form_action_id').read()[0]
            action['domain'] = [('state', '=', 'approved')]
        elif self.model_name == 'Grab Request Form':
            action = self.env.ref('dex_form_request_approval.grab_request_form_form_action_id').read()[0]
            action['domain'] = [('state', '=', 'approved')]
        #         elif self.model_name == 'Official Business Form':
        #             action = self.env.ref('dex_form_request_approval.official_business_form_action_id').read()[0]
        #             action['domain'] = [('state', '=', 'approved')]
        elif self.model_name == 'On Line Purchases':
            action = self.env.ref('dex_form_request_approval.online_purchases_form_action_id').read()[0]
            action['domain'] = [('state', '=', 'approved')]
        #         elif self.model_name == 'Overtime Authorization Form':
        #             action = self.env.ref('dex_form_request_approval.overtime_authorization_form_action_id').read()[0]
        #             action['domain'] = [('state', '=', 'approved')]
        elif self.model_name == 'Request For Cash Advance':
            action = self.env.ref('dex_form_request_approval.request_for_cash_advance_form_action_id').read()[0]
            action['domain'] = [('state', '=', 'approved')]
        elif self.model_name == 'It Request Form':
            action = self.env.ref('dex_form_request_approval.it_request_form_action_id').read()[0]
            action['domain'] = [('state', '=', 'approved')]
        elif self.model_name == 'Transport Network Vehicle Form':
            action = self.env.ref('dex_form_request_approval.transport_network_vehicle_form_action_id').read()[0]
            action['domain'] = [('state', '=', 'approved')]
        elif self.model_name == 'Payment Request Form':
            action = self.env.ref('dex_form_request_approval.payment_request_form_action_id').read()[0]
            action['domain'] = [('state', '=', 'approved')]
        else:
            action = self.env.ref('dex_form_request_approval.view_preview_dashboard_kanban').read()[0]
        return action

    def draft(self):
        if self.model_name == 'Client Pick Up Permit':
            action = self.env.ref('dex_form_request_approval.client_pickup_permit_form_action_id').read()[0]
            action['domain'] = [('state', '=', 'draft')]
        elif self.model_name == 'Gasoline Allowance Form':
            action = self.env.ref('dex_form_request_approval.gasoline_allowance_form_action_id').read()[0]
            action['domain'] = [('state', '=', 'draft')]
        elif self.model_name == 'Grab Request Form':
            action = self.env.ref('dex_form_request_approval.grab_request_form_form_action_id').read()[0]
            action['domain'] = [('state', '=', 'draft')]
        #         elif self.model_name == 'Official Business Form':
        #             action = self.env.ref('dex_form_request_approval.official_business_form_action_id').read()[0]
        #             action['domain'] = [('state', '=', 'draft')]
        elif self.model_name == 'On Line Purchases':
            action = self.env.ref('dex_form_request_approval.online_purchases_form_action_id').read()[0]
            action['domain'] = [('state', '=', 'draft')]
        #         elif self.model_name == 'Overtime Authorization Form':
        #             action = self.env.ref('dex_form_request_approval.overtime_authorization_form_action_id').read()[0]
        #             action['domain'] = [('state', '=', 'draft')]
        elif self.model_name == 'Request For Cash Advance':
            action = self.env.ref('dex_form_request_approval.request_for_cash_advance_form_action_id').read()[0]
            action['domain'] = [('state', '=', 'draft')]
        elif self.model_name == 'It Request Form':
            action = self.env.ref('dex_form_request_approval.it_request_form_action_id').read()[0]
            action['domain'] = [('state', '=', 'draft')]
        elif self.model_name == 'Transport Network Vehicle Form':
            action = self.env.ref('dex_form_request_approval.transport_network_vehicle_form_action_id').read()[0]
            action['domain'] = [('state', '=', 'draft')]
        elif self.model_name == 'Payment Request Form':
            action = self.env.ref('dex_form_request_approval.payment_request_form_action_id').read()[0]
            action['domain'] = [('state', '=', 'draft')]
        else:
            action = self.env.ref('dex_form_request_approval.view_preview_dashboard_kanban').read()[0]
        return action

    def view_for_review(self):
        self.name = self.env.context.get('active_model')
        print(self.model_name)
        if self.model_name == 'Client Pick Up Permit':
            action = self.env.ref('dex_form_request_approval.client_pickup_permit_form_action_id').read()[0]
        elif self.model_name == 'Gasoline Allowance Form':
            action = self.env.ref('dex_form_request_approval.gasoline_allowance_form_action_id').read()[0]
        elif self.model_name == 'Grab Request Form':
            action = self.env.ref('dex_form_request_approval.grab_request_form_form_action_id').read()[0]
        #         elif self.model_name == 'Official Business Form':
        #             action = self.env.ref('dex_form_request_approval.official_business_form_action_id').read()[0]
        elif self.model_name == 'On Line Purchases':
            action = self.env.ref('dex_form_request_approval.online_purchases_form_action_id').read()[0]
        #         elif self.model_name == 'Overtime Authorization Form':
        #             action = self.env.ref('dex_form_request_approval.overtime_authorization_form_action_id').read()[0]
        elif self.model_name == 'Request For Cash Advance':
            action = self.env.ref('dex_form_request_approval.request_for_cash_advance_form_action_id').read()[0]
        elif self.model_name == 'It Request Form':
            action = self.env.ref('dex_form_request_approval.it_request_form_action_id').read()[0]
        elif self.model_name == 'Transport Network Vehicle Form':
            action = self.env.ref('dex_form_request_approval.transport_network_vehicle_form_action_id').read()[0]
        elif self.model_name == 'Payment Request Form':
            action = self.env.ref('dex_form_request_approval.payment_request_form_action_id').read()[0]
        else:
            action = self.env.ref('dex_form_request_approval.view_preview_dashboard_kanban').read()[0]
        return action

    def get_action_request(self, xml_id):
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'client.pick.up.permit',
            'view_id': self.env.ref(xml_id).id,
        }

    def _update_record(self, field_name, total_count, model_title):
        model_name = re.sub(r'[.-]', ' ', model_title).title()
        try:
            existing_records = self.env['preview.dashboard'].search([('name', '=', model_title)])
            if existing_records:
                for existing_record in existing_records:
                    existing_record.write({field_name: total_count, 'model_name': model_name})
            else:
                # Check if there is any record with the same field_name values to avoid duplication
                existing_record_with_same_values = self.env['preview.dashboard'].search([
                    (field_name, '=', total_count),
                    ('model_name', '=', model_name),
                ])
                if not existing_record_with_same_values:
                    self.env['preview.dashboard'].create({
                        'name': model_title,
                        'model_name': model_name,
                        field_name: total_count,
                    })
                else:
                    # If a record with the same values already exists, update its name
                    for existing_record in existing_record_with_same_values:
                        existing_record.write({'name': model_title})
        except Exception as e:
            # Handle exception gracefully, log it or print it
            print(f"Error while updating record for {model_title}: {e}")


class PreviewDashboardLines(models.Model):
    _name = 'preview.dashboard.lines'
    _description = 'Dashboard Preview Lines'

    name = fields.Char()
    preview_dashboard_ids = fields.Many2one('preview.dashboard', string='Preview Dashboard')

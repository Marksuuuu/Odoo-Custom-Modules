# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)

class AgreementWizard(models.TransientModel):
    _name = 'agreement.wizard'

    agreement_text = fields.Char(string="Reason")
    name_of_person = fields.Many2one('hr.employee', string='Name of Person')
    unit = fields.Many2one('asset', string='Asset')

    serial_number = fields.Char(related='unit.serial_num', string='Serial Number', store=True)

    charger_with_usb_cable = fields.Char(related='unit.charger_with_usb_cable', string='Charger with usb cable')

    is_have_postpaid_number = fields.Boolean(related='unit.is_have_postpaid_number', default=False,
                                             string='Is have Postpaid Number')

    other_peripherals = fields.Char(related='unit.other_peripherals', string='Other Peripherals')

    remarks = fields.Char(related='unit.remarks', string='Remarks')

    digital_signature = fields.Binary(string="Signature", stored=True)

    department_of_person = fields.Many2one(related='name_of_person.department_id')






    def view_agreement(self):
        active_id = self._context.get('active_id')
        active_model = self.env.context.get('active_model')
        requests_res = self.env[active_model].browse(active_id)

        test = requests_res.name_of_person
        _logger.info(f'TESTTTT {test}')
        _
        #
        # if requests_res:
        #     vals = {
        #         'cancelled_by': self.env.user.id,
        #         'cancellation_reason': self.cancellation_rsn,
        #         'cancelled_date': fields.Datetime.now(),
        #         'approval_status': 'cancel',
        #         'approval_link': False,
        #         'state': 'cancel'
        #     }
        #
        #     requests_res.write(vals)

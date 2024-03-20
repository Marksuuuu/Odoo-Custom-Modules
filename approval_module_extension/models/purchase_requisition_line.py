from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError
import os
import base64
import datetime
import hashlib
import os
import re
import smtplib


class PurchaseRequisitionLine(models.Model):
    _inherit = 'purchase.requisition.line'
    _description = 'Inherited Purchase Requisition Line'

    description = fields.Char(string='Description')
    reference_doc = fields.Many2many("ir.attachment", string='Reference Doc.', required=True, store=True)
    file_links = fields.Text(string='File Links', compute='_compute_file_links',
                             store=True)

    @api.onchange('product_id')
    def product_onchange(self):
        for rec in self.product_id:
            def_code = '[' + rec.default_code + ']' if rec.default_code else ''
            self.description = "{} {}".format(def_code, rec.name)

    @api.constrains('reference_doc')
    def _check_reference_doc(self):
        for record in self:
            for attachment in record.reference_doc:
                # Check if the attachment is a PDF
                if not self._is_pdf(attachment.datas):
                    raise ValidationError('Only PDF files are allowed for reference documents!')

    @staticmethod
    def _is_pdf(file_content):
        # Decode the base64 string before checking for PDF header
        decoded_content = base64.b64decode(file_content)
        # Perform a simple check to see if the file content indicates a PDF
        return decoded_content.startswith(b'%PDF-')

    @api.depends('reference_doc')
    def _compute_file_links(self):
        for record in self:
            acc_attachments = self.env['purchase.requisition.attachments']
            links = []
            for attachment in record.reference_doc:
                link = self.get_file_link(attachment)
                links.append(self.get_file_link(attachment))
                print(self.requisition_id.id)
                print(attachment.id)
                acc_attachments.create({
                    'pr_ids': self.requisition_id.id,
                    'product_id': self.product_id.id,
                    'attachments_ids': attachment.id,
                    'file_links': link  # Set file_links for each attachment individually
                })
                record.file_links = '\n'.join(links)

    def get_module_static_path(self):
        module_path = os.path.dirname(os.path.realpath(__file__))
        static_path = os.path.join(module_path, '../static', 'uploads')

        if not os.path.exists(static_path):
            os.makedirs(static_path)

        return static_path

    def create(self, vals):
        record = super(PurchaseRequisitionLine, self).create(vals)
        self.save_files_to_static_folder(record)
        # Check if record is a boolean
        if isinstance(record, bool):
            # Handle the case where record is a boolean (True or False)
            # You may want to add appropriate logic for this case.
            pass
        elif record.reference_doc:
            attachments = self.env['ir.attachment'].browse(record.reference_doc.ids)
            attachments.write({'public': True, 'res_id': record.id})
        return record

    def write(self, vals):
        result = super(PurchaseRequisitionLine, self).write(vals)
        if result:
            self.save_files_to_static_folder(result)
            if isinstance(result, bool):
                # Handle the case where record is a boolean (True or False)
                # You may want to add appropriate logic for this case.
                pass
            elif result.reference_doc:
                attachments = self.env['ir.attachment'].browse(result.reference_doc.ids)
                attachments.write({'public': True, 'res_id': result.id})
            return result

    def save_files_to_static_folder(self, record):
        static_folder_path = self.get_module_static_path()

        # Check if record is a boolean
        if isinstance(record, bool):
            # Handle the case where record is a boolean (True or False)
            # You may want to add appropriate logic for this case.
            pass
        elif record.reference_doc:
            # Proceed with the existing logic for non-boolean records
            for attachment in record.reference_doc:
                file_data = attachment.datas
                if file_data:
                    file_name = self.generate_unique_filename(attachment.name)
                    file_path = os.path.join(static_folder_path, file_name)
                    with open(file_path, 'wb') as file:
                        file.write(base64.b64decode(file_data))

                    # Update the attachment record with the correct store_fname
                    attachment.write({'store_fname': file_name})

    def generate_unique_filename(self, original_filename):
        unique_id = hashlib.sha256(os.urandom(8)).hexdigest()[:8]
        filename, extension = os.path.splitext(original_filename)
        return f"{filename}_{unique_id}{extension}"

    def get_file_link(self, attachment):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return f"{base_url}/web/content/{attachment.id}/{attachment.name}"

import base64
import datetime
import hashlib
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero


class InheritStockPicking(models.Model):
    _inherit = 'stock.picking'
    _description = 'Inherited Stock Picking'

    stock_picking_attach = fields.One2many(
        'stock.picking.attachments', 'stock_picking_attach_ids', string='Stock Attachments')

    attachments_ids = fields.Many2one(
        'ir.attachment', string='Attachments')
    file_links = fields.Char(string='File Links')

    check_if_receipts = fields.Boolean(
        string='Check if Receipts',
        compute='_compute_check_if_receipts',
    )

    check_if_here = fields.Boolean(
        string='Check if Receipts',
        compute='_compute_check_if_here',
    )

    check_if_wiv = fields.Boolean(compute='_compute_check_if_wiv', string='Check if Wiv', default=False)

    check_if_else = fields.Boolean(compute='_compute_check_if_else', string='Check if Else', default=False)

    check_if_else = fields.Boolean(compute='_compute_check_if_else', string='Check if Else', default=False)

    check_if_pick = fields.Boolean(compute='_compute_check_if_pick', string='Check if Pick', default=False)

    ###### FIELDS FOR ELSE WH #######
    payment_term_id = fields.Many2one(
        'account.payment.term', string='Payment Terms', check_company=True,  # Unrequired company
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", )

    invoice_date = fields.Date(string='Invoice/Bill Date', index=True, copy=False)

    carrier_id = fields.Many2one("delivery.carrier", string="Carrier", check_company=True)

    forwarder = fields.Char(string='Forwarder')

    flt_vessel = fields.Char(string='Flt/Vessel')

    hawb = fields.Char(string='HawB No.')

    mawb = fields.Char(string='MawB No.')

    custodian = fields.Many2one('hr.employee', string='Custodian')

    request_by = fields.Many2one('hr.employee', string='Request By')

    verified_by = fields.Many2one('hr.employee', string='Verified By')

    def print_invoice_voucher(self):
        return self.env.ref('approval_module_extension.inventory_invoice_voucher').report_action(self)

    def print_picking_components(self):
        return self.env.ref('approval_module_extension.picking_operations').report_action(self)

    @api.depends('picking_type_id', 'check_if_wiv')
    def _compute_check_if_wiv(self):
        for rec in self:
            if rec.picking_type_id.name == "WIV Request":
                print(rec.check_if_wiv)
                rec.check_if_wiv = True
                for move_ids in rec.move_line_ids_without_package:
                    move_ids.write({
                        'check_if_shipping_or_transfer': True
                    })
            else:
                print(rec.check_if_wiv)
                rec.check_if_wiv = False
                for move_ids in rec.move_line_ids_without_package:
                    move_ids.write({
                        'check_if_shipping_or_transfer': False
                    })

    @api.depends('picking_type_id', 'check_if_else')
    def _compute_check_if_else(self):
        for rec in self:
            if rec.picking_type_id.name == "ELSE WH":
                print(rec.check_if_else)
                rec.check_if_else = True
            else:
                print(rec.check_if_else)
                rec.check_if_else = False

    @api.depends('picking_type_id', 'check_if_pick')
    def _compute_check_if_pick(self):
        for rec in self:
            if rec.picking_type_id.name == "Pick Components":
                print(rec.check_if_pick)
                rec.check_if_pick = True
            else:
                print(rec.check_if_pick)
                rec.check_if_pick = False

    @api.depends('picking_type_id', 'check_if_else')
    def get_picking_type(self):
        for rec in self:
            if rec.picking_type_id.name == "ELSE WH":
                return "<span>ELSE WH</span>"
            elif rec.picking_type_id.name == "Line Return":
                return "<span>Line Return</span>"
            elif rec.picking_type_id.name == "WIV Request":
                return "<span>WIV Request</span>"
            elif rec.picking_type_id.name == "Warehouse - Receipts":
                return "<span>Warehouse - Receipts</span>"
            elif rec.picking_type_id.name == "Scrap to good":
                return "<span>Scrap to good</span>"
            elif rec.picking_type_id.name == "Warehouse - Material Issuance":
                return "<span>Warehouse - Material Issuance</span>"
            elif rec.picking_type_id.name == "Warehouse - Internal Transfers":
                return "<span>Warehouse - Internal Transfers</span>"
            elif rec.picking_type_id.name == "Manufacturing - FG to Residual":
                return "<span>Manufacturing - FG to Residual</span>"
            else:
                return "<span>N/A</span>"

    @api.depends('picking_type_id')
    def _compute_check_if_receipts(self):
        warehouse_receipts = self.filtered(lambda rec: rec.picking_type_id.name == 'Warehouse - Receipts')
        for rec in self - warehouse_receipts:
            rec.check_if_receipts = False
        warehouse_receipts.check_if_receipts = True

    @api.depends('picking_type_id')
    def _compute_check_if_here(self):
        for rec in self:
            if rec.picking_type_id.name in [
                'Scrap to good',
                'Line Return',
                'WIV Request',
                'Material Issuance',
            ]:
                rec.check_if_here = True
                print('asdasd', rec.check_if_here)
            else:
                print('asdasd', rec.check_if_here)
                rec.check_if_here = False

    def function_to_trigger_notify(self):
        for rec in self:
            rec.notify_requester_now()

    def button_validate(self):
        self.ensure_one()
        # Why I create new function to call that notify request. because to prevent multiple email send at once
        self.function_to_trigger_notify()
        if not self.move_lines and not self.move_line_ids:
            raise UserError(_('Please add some items to move.'))

        # Clean-up the context key at validation to avoid forcing the creation of immediate
        # transfers.
        ctx = dict(self.env.context)
        ctx.pop('default_immediate_transfer', None)
        self = self.with_context(ctx)

        # add user as a follower
        self.message_subscribe([self.env.user.partner_id.id])

        # If no lots when needed, raise error
        picking_type = self.picking_type_id
        precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        no_quantities_done = all(float_is_zero(move_line.qty_done, precision_digits=precision_digits) for move_line in
                                 self.move_line_ids.filtered(lambda m: m.state not in ('done', 'cancel')))
        no_reserved_quantities = all(
            float_is_zero(move_line.product_qty, precision_rounding=move_line.product_uom_id.rounding) for move_line in
            self.move_line_ids)
        if no_reserved_quantities and no_quantities_done:
            raise UserError(
                _('You cannot validate a transfer if no quantites are reserved nor done. To force the transfer, switch in edit more and encode the done quantities.'))

        if picking_type.use_create_lots or picking_type.use_existing_lots:
            lines_to_check = self.move_line_ids
            if not no_quantities_done:
                lines_to_check = lines_to_check.filtered(
                    lambda line: float_compare(line.qty_done, 0,
                                               precision_rounding=line.product_uom_id.rounding)
                )

            for line in lines_to_check:
                product = line.product_id
                if product and product.tracking != 'none':
                    if not line.lot_name and not line.lot_id:
                        raise UserError(
                            _('You need to supply a Lot/Serial number for product %s.') % product.display_name)

        # Propose to use the sms mechanism the first time a delivery
        # picking is validated. Whatever the user's decision (use it or not),
        # the method button_validate is called again (except if it's cancel),
        # so the checks are made twice in that case, but the flow is not broken
        sms_confirmation = self._check_sms_confirmation_popup()
        if sms_confirmation:
            return sms_confirmation

        if no_quantities_done:
            view = self.env.ref('stock.view_immediate_transfer')
            wiz = self.env['stock.immediate.transfer'].create({'pick_ids': [(4, self.id)]})
            return {
                'name': _('Immediate Transfer?'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'stock.immediate.transfer',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'res_id': wiz.id,
                'context': self.env.context,
            }

        if self._get_overprocessed_stock_moves() and not self._context.get('skip_overprocessed_check'):
            view = self.env.ref('stock.view_overprocessed_transfer')
            wiz = self.env['stock.overprocessed.transfer'].create({'picking_id': self.id})
            return {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'stock.overprocessed.transfer',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'res_id': wiz.id,
                'context': self.env.context,
            }

        # Check backorder should check for other barcodes
        if self._check_backorder():
            return self.action_generate_backorder_wizard()
        self.action_done()
        return

    def get_requesters_email(self):
        for rec in self:
            if rec.user_id.login:
                print(rec.user_id.login)
                return rec.user_id.login

    def notify_requester_now(self):
        self.ensure_one()
        sender = 'noreply@teamglac.com'
        host = "192.168.1.114"
        port = 25
        username = "noreply@teamglac.com"
        password = "noreply"

        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        token = self.generate_token()

        approval_url = "{}/approval_module_extension/request/approve/{}".format(base_url, token)
        disapproval_url = "{}/approval_module_extension/request/disapprove/{}".format(base_url, token)

        wiv_url = "{}/approval_module_extension/request/wiv/{}".format(base_url, token)
        dashboard_url = "{}/approval_module_extension/request/dashboard/{}".format(base_url, token)

        self.write({'approval_link': token})

        msg = MIMEMultipart()
        msg['From'] = formataddr(('Odoo Mailer', sender))
        msg['To'] = self.user_id.login
        msg['Subject'] = 'Inventory Request [' + self.name + '] are now Validated!'

        html_content = """
                    <!DOCTYPE html>
                    <html>
                    <head>
                    <style>
                    table {
                      border-collapse: collapse;
                      width: 100%;
                      font-size: 16px;
                    }

                    * {
                      font-size: 16px;
                    }

                    th, td {
                      text-align: left;
                      padding: 10px;
                    }

                    tr:nth-child(even){background-color: #f2f2f2}

                    th {
                      background-color: #5f5e97;
                      color: white;
                    }
                    .button {
                      background-color: #04AA6D; /* Green */
                      border: none;
                      color: white;
                      padding: 15px 32px;
                      text-align: center;
                      text-decoration: none;
                      display: inline-block;
                      font-size: 16px;
                      margin: 4px 2px;
                      cursor: pointer;
                    }
                    .button2 {background-color: #008CBA;} /* Blue */
                    .button3 {background-color: #f44336;} /* Red */ 
                    .button4 {background-color: #e7e7e7; color: black;} /* Gray */ 
                    .button5 {background-color: #555555;} /* Black */
                    </style>
                    </head>
                    <body>
                """

        html_content += f"""
                    <dt style='text-transform: uppercase;'>This item (<b>{self.name}</b>) is now Validated. Please check if there is any problem.</dt>
                    <br></br>
                    <dd>Requested by: &nbsp;&nbsp;{self.user_id.name if self.name != False else ""}</dd>
                    <dd>Date Requested: &nbsp;&nbsp;{datetime.datetime.now() if self.name != False else ""}</dd>
                    <dd>Source Document: &nbsp;&nbsp;{self.origin if self.origin != False else ""}</dd>
                    <br></br>
                    <span><b>ITEMS REQUESTED</b></span>
                    <br/>
                    <br></br>
                """

        html_content += """
                    <table style='margin-bottom: 50px;'>
                        <tr>
                            <th>Product</th>
                            <th>Description</th>
                            <th>Quantity</th>
                            <th>EOH</th>
                            <th>Remarks</th>
                        </tr>
                """

        for line in self.move_line_ids_without_package:
            html_content += f"""
                        <tr>
                            <td>{line.product_id.name}</td>
                            <td>{line.product_id.name + '[' + line.product_id.name + ']'}</td>
                            <td>{line.qty_done}</td>
                             <td>{line.product_id.qty_available}</td>
                            <td>{self.note}</td>
                        </tr>
                    """

        html_content += f"""
                                    </table>

                                    <a href="{wiv_url}" style='background-color: blue;
                                        border: none;
                                        color: white;
                                        text-align: center;
                                        text-decoration: none;
                                        display: inline-block;
                                        font-size: 16px;
                                        margin: 4px 2px;
                                        padding: 10px 24px;
                                        border-radius: 50px;
                                        cursor: pointer;'>ODOO {self.get_picking_type()} FORM</a>

                                    <a href="{dashboard_url}" style='background-color: yellow;
                                        border: none;
                                        color: black;
                                        text-align: center;
                                        text-decoration: none;
                                        display: inline-block;
                                        font-size: 16px;
                                        margin: 4px 2px;
                                        padding: 10px 24px;
                                        border-radius: 50px;
                                        cursor: pointer;'>ODOO APPROVAL DASHBOARD</a>
                                    </body>
                                    </html>
                                """

        msg.attach(MIMEText(html_content, 'html'))

        try:
            smtpObj = smtplib.SMTP(host, port)
            smtpObj.login(username, password)
            smtpObj.sendmail(sender, self.user_id.login, msg.as_string())

            msg = "Successfully sent email"
            return {
                'success': {
                    'title': 'Successfully email sent!',
                    'message': f'{msg}'}
            }
        except Exception as e:
            msg = f"Error: Unable to send email: {str(e)}"
            return {
                'warning': {
                    'title': 'Error: Unable to send email!',
                    'message': f'{msg}'}
            }

        # Next Approver Sending of Email


class InheritStockMoveLine(models.Model):
    _inherit = 'stock.move.line'
    _description = 'Inherited Stock Move'

    reference_doc = fields.Many2many("ir.attachment", string='Reference Doc.', required=True, store=True)
    file_links = fields.Text(string='File Links', compute='_compute_file_links',
                             store=True)

    @api.model
    def create(self, vals):
        record = super(InheritStockMoveLine, self).create(vals)
        record._check_ref_docs()

        return record

    def write(self, values):
        res = super(InheritStockMoveLine, self).write(values)
        self._check_ref_docs()
        return res

    def _check_ref_docs(self):
        if not self.move_line_nosuggest_ids.reference_doc:
            raise UserError(
                "Please note that data must be provided in the required fields to proceed. Missing Reference Doc")

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
            acc_attachments = self.env['stock.picking.attachments']
            links = []

            # Get existing attachments for this record
            existing_attachments = acc_attachments.search([
                ('stock_move_line_attach_ids', '=', record.id),
                ('stock_picking_attach_ids', '=', self.picking_id.id),
            ])

            # Delete existing attachments that are not in the new reference_doc
            attachments_to_delete = existing_attachments.filtered(
                lambda att: att.attachments_ids not in record.reference_doc
            )
            attachments_to_delete.sudo().unlink()  # Use sudo to bypass access rights

            for attachment in record.reference_doc:
                link = self.get_file_link(attachment)

                # Check if the link contains "NewId origin="
                # and if the document does not already exist
                if "NewId origin=" not in link and not self.document_exists(link):
                    links.append(link)

                    acc_attachments.create({
                        'stock_picking_attach_ids': self.picking_id.id,
                        'stock_move_line_attach_ids': self.id,
                        'product_id': self.product_id.id,
                        'attachments_ids': attachment.id,
                        'file_links': link  # Set file_links for each attachment individually
                    })

            record.file_links = '\n'.join(links)

    def document_exists(self, link):
        # Implement logic to check if the document with the given link already exists
        # For example, you can use a search query to check for existing entries
        existing_attachment = self.env['stock.picking.attachments'].search([
            ('file_links', '=', link),
            ('stock_move_line_attach_ids', '=', self.id),
            ('stock_picking_attach_ids', '=', self.picking_id.id),
        ])
        return bool(existing_attachment)

    def unlink(self):
        # Delete related stock.picking.attachments records when unlinking your model
        attachments_to_delete = self.env['stock.picking.attachments'].search([
            ('stock_move_line_attach_ids', 'in', self.ids),
            ('stock_picking_attach_ids', '=', self.picking_id.id),
        ])
        attachments_to_delete.unlink()

        return super(InheritStockMoveLine, self).unlink()

    def get_module_static_path(self):
        module_path = os.path.dirname(os.path.realpath(__file__))
        static_path = os.path.join(module_path, '../static', 'uploads')

        if not os.path.exists(static_path):
            os.makedirs(static_path)

        return static_path

    def create(self, vals):
        record = super(InheritStockMoveLine, self).create(vals)
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
        result = super(InheritStockMoveLine, self).write(vals)
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


class StockPickingAttachments(models.Model):
    _name = 'stock.picking.attachments'
    _description = 'Stock Picking Attachments'

    stock_picking_attach_ids = fields.Many2one(
        'stock.picking', string='Stock Picking Connection')
    stock_move_line_attach_ids = fields.Many2one('stock.move.line', string='Stock Move')
    product_id = fields.Many2one('product.product', string='Product')
    attachments_ids = fields.Many2one(
        'ir.attachment', string='Attachments')
    file_links = fields.Char(string='File Links')

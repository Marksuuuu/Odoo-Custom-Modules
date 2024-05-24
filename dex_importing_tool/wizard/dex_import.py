# -*- coding: utf-8 -*-
from odoo import models, fields, api
import base64
import pandas as pd
import logging

_logger = logging.getLogger(__name__)


class DexImport(models.TransientModel):
    _name = 'dex.import'

    xlsx_file = fields.Binary('XLSX File')

    def download_excel(self):
        # Generate the URL for the controller method
        url = '/dex/import/download'
        # Redirect to the URL
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'self',
        }

    def import_excel(self):
        # Read the file
        if self.xlsx_file:
            try:
                file_content = base64.b64decode(self.xlsx_file)
                df = pd.read_excel(file_content, engine='openpyxl')
                # Iterate over the rows of the dataframe and create or update records
                for index, row in df.iterrows():
                    # Check if EDP exists in the dataframe
                    if 'EDP' in row:
                        # Assuming YourModel is the model where you want to update fields
                        model_objs = self.env['product.template'].search([('default_code', '=', row['EDP'])])
                        for model_obj in model_objs:
                            _logger.info(f'Logssss, {model_obj}')
                            # Update the fields
                            model_obj.write({
                                'length_mm': row.get('LENGTH (MM)'),
                                'width_mm': row.get('WIDTH (MM)'),
                                'height_mm': row.get('HEIGHT (MM)'),
                                'thickness_mm': row.get('THICKNESS (MM)'),
                            })
            except Exception as e:
                # Log the exception or handle it appropriately
                # For now, just print the exception
                _logger.info(f"Error occurred while importing Excel file: {str(e)}")

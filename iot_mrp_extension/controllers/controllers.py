from odoo import http
from odoo.http import request
import json
import logging
import requests

_logger = logging.getLogger(__name__)

class IotMrp(http.Controller):

    @http.route('/lms-login', type='http', auth='public', website=True)
    def display_mrp_production_table(self, search_input=None, **kw):
        try:
            mrp_workcenter_productivity = request.env['mrp.workcenter.productivity'].sudo().search([])

            if search_input:
                employee_id_no = self._search_function(search_input)
                if employee_id_no:
                    # Set session if authentication is successful
                    request.session['authenticated'] = True
                    request.session['employee_id_no'] = employee_id_no

                    # Redirect to the welcome page after successful login
                    return request.redirect('/index', code=303)

            return request.render('iot_mrp_extension.main_template_id',
                                  {'mrp_workcenter_productivity': mrp_workcenter_productivity})

        except Exception as e:
            _logger.exception("Error in display_mrp_production_table: %s", e)
            return request.render('iot_mrp_extension.main_template_id', {'error_message': str(e)})

    @http.route('/index', type='http', auth='public', website=True)
    def redirect_to_index(self, search_input=None, **kw):
        try:
            # Check if the user is authenticated
            if request.session.get('authenticated'):
                employee_id_no = request.session.get('employee_id_no')

                if employee_id_no:
                    # Make API call to fetch data based on employee_id_no
                    hris_api = f'http://hris.teamglac.com/api/users/emp-num?empno={employee_id_no}'
                    link = 'http://hris.teamglac.com/'
                    response = requests.get(hris_api)

                    if response.status_code == 200:
                        # Parse the API response (assuming it's JSON)
                        hris_data = json.loads(response.text)['result']
                        photo_url = link + hris_data['photo_url']
                        print(f"💻==>> photo_url: {photo_url}")

                        # Pass HRIS data to the render method
                        return request.render('iot_mrp_extension.page_index_id',
                                              {'employee_id_no': employee_id_no,
                                               'hris_data': hris_data})
                    else:
                        # Handle API error or non-OK status code
                        _logger.warning("Failed to fetch data from HRIS API. Status code: %s", response.status_code)
                        return request.render('iot_mrp_extension.main_template_id', {'error_message': 'Failed to fetch HRIS data'})
                else:
                    return request.render('iot_mrp_extension.main_template_id', {'error_message': 'Employee ID not found'})
            else:
                # Redirect to the login page if not authenticated
                return request.redirect('/lms-login', code=303)

        except Exception as e:
            _logger.exception("Error in redirect_to_index: %s", e)
            return request.render('iot_mrp_extension.main_template_id', {'error_message': str(e)})

    def _search_function(self, search_input):
        try:
            with open('mark-folder/iot_mrp_extension/static/personnel_employee.json', 'r') as file:
                data = json.load(file)
                for item in data.get('result', []):
                    for key, employee_list in item.items():
                        if key == str(search_input):
                            # Assuming there is only one item in the list
                            first_employee_data = employee_list[0]
                            if "employee_id_no" in first_employee_data:
                                return first_employee_data["employee_id_no"]

                # Return None if the key is not found
                return None

        except Exception as e:
            _logger.exception("Error in _search_function: %s", e)
            return None

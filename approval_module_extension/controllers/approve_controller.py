from odoo import http
from odoo.http import request

INVALID_LINK = "Invalid approval link!"


class RequestApprovalController(http.Controller):
    # PURCHASE REQUISITION
    @http.route('/purchase_requisition/request/approve/<string:token>', type='http', auth='public', website=True)
    def pr_request_approval(self, token):
        request_form = request.env['purchase.requisition'].sudo().search([('approval_link', '=', token)])
        if request_form:
            request_form.pr_approve_request()
            msg = "Request approved successfully!"
            return f"""<script>alert("{msg}");window.close();</script>"""

        else:
            return INVALID_LINK


    @http.route('/purchase_requisition/request/disapprove/<string:token>', type='http', auth='public', website=True,
                csrf=False,
                method=['GET', 'POST'])
    def pr_request_disapproval(self, token, **post):
        request_form = request.env['purchase.requisition'].sudo().search([('approval_link', '=', token)])
        if request_form:
            if request.httprequest.method == 'POST' and 'reason' in post:
                reason = post.get('reason')
                request_form.write(
                    {'state': 'disapprove', 'approval_status': 'disapprove', 'disapproval_reason': reason})
                return """<script>window.close();</script>"""
            else:
                return """
                    <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <meta http-equiv="X-UA-Compatible" content="IE=edge">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>Document</title>
                        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css">
                    </head>
                    <body>
                        <div class="container">
                            <div class="justify-content-center"> 
                                <div class="modal" tabindex="-1" id="modal-show">
                                    <div class="modal-dialog">
                                      <div class="modal-content">
                                        <div class="modal-header">
                                          <h5 class="modal-title">Disapproved Reason</h5>
                                        </div>
                                        <form method="post">
                                        <div class="modal-body">
                                                <textarea class="form-control"type="text" name="reason" placeholder="Reason here" id="text-area"></textarea>
                                        </div>
                                        <div class="modal-footer">
                                          <button type="submit" class="btn btn-danger" id="saved-btn">Save</button>
                                        </div>
                                    </form>
                                      </div>
                                    </div>
                                  </div>
                            </div>
                        </div>

                    </body>
                    <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.9.1/dist/umd/popper.min.js" integrity="sha384-SR1sx49pcuLnqZUnnPwx6FCym0wLsk5JZuNx2bPPENzswTNFaQU1RDvt3wT4gWFG" crossorigin="anonymous"></script>
                    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta3/dist/js/bootstrap.min.js" integrity="sha384-j0CNLUeiqtyaRmlzUHCPZ+Gy5fQu0dQ6eZ/xAww941Ai1SxSY+0EQqNXNE6DZiVc" crossorigin="anonymous"></script>
                    <script src="https://code.jquery.com/jquery-3.5.1.min.js"></script>
                    <script>
                        $(document).ready(function(){
                            $('#modal-show').show()

                        $('#saved-btn').click(function(){
                            var text_area = $('#text-area').val()
                            if(text_area == ''){
                                alert('Enter Something')
                                console.log(text_area)
                                return false;
                            }else{
                                alert('Success')
                                console.log(text_area)
                            }
                        })

                        });
                    </script>
                    </html>
                    """
        else:
            return INVALID_LINK

    # PURCHASE ORDER
    @http.route('/purchase_order/request/approve/<string:token>', type='http', auth='public', website=True)
    def po_request_approval(self, token):
        request_form = request.env['purchase.order'].sudo().search([('approval_link', '=', token)])
        if request_form:
            request_form.po_approve_request()
            msg = "Request approved successfully!"
            return f"""<script>alert("{msg}");window.close();</script>"""
        else:
            return INVALID_LINK

    @http.route('/purchase_order/request/disapprove/<string:token>', type='http', auth='public', website=True,
                csrf=False,
                method=['GET', 'POST'])
    def po_request_disapproval(self, token, **post):
        request_form = request.env['purchase.order'].sudo().search([('approval_link', '=', token)])
        if request_form:
            if request.httprequest.method == 'POST' and 'reason' in post:
                reason = post.get('reason')
                request_form.write(
                    {'state': 'disapprove', 'approval_status': 'disapprove', 'disapproval_reason': reason})
                return """<script>window.close();</script>"""
            else:
                return """
                        <html lang="en">
                        <head>
                            <meta charset="UTF-8">
                            <meta http-equiv="X-UA-Compatible" content="IE=edge">
                            <meta name="viewport" content="width=device-width, initial-scale=1.0">
                            <title>Document</title>
                            <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css">
                        </head>
                        <body>
                            <div class="container">
                                <div class="justify-content-center">
                                    <div class="modal" tabindex="-1" id="modal-show">
                                        <div class="modal-dialog">
                                          <div class="modal-content">
                                            <div class="modal-header">
                                              <h5 class="modal-title">Disapproved Reason</h5>
                                            </div>
                                            <form method="post">
                                            <div class="modal-body">
                                                    <textarea class="form-control"type="text" name="reason" placeholder="Reason here" id="text-area"></textarea>
                                            </div>
                                            <div class="modal-footer">
                                              <button type="submit" class="btn btn-danger" id="saved-btn">Save</button>
                                            </div>
                                        </form>
                                          </div>
                                        </div>
                                      </div>
                                </div>
                            </div>

                        </body>
                        <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.9.1/dist/umd/popper.min.js" integrity="sha384-SR1sx49pcuLnqZUnnPwx6FCym0wLsk5JZuNx2bPPENzswTNFaQU1RDvt3wT4gWFG" crossorigin="anonymous"></script>
                        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta3/dist/js/bootstrap.min.js" integrity="sha384-j0CNLUeiqtyaRmlzUHCPZ+Gy5fQu0dQ6eZ/xAww941Ai1SxSY+0EQqNXNE6DZiVc" crossorigin="anonymous"></script>
                        <script src="https://code.jquery.com/jquery-3.5.1.min.js"></script>
                        <script>
                            $(document).ready(function(){
                                $('#modal-show').show()

                            $('#saved-btn').click(function(){
                                var text_area = $('#text-area').val()
                                if(text_area == ''){
                                    alert('Enter Something')
                                    console.log(text_area)
                                    return false;
                                }else{
                                    alert('Success')
                                    console.log(text_area)
                                }
                            })

                            });
                        </script>
                        </html>
                        """
        else:
            return INVALID_LINK

    @http.route('/approval_module_extension/request/dashboard/<string:token>', type='http', auth='public', website=True)
    def dashboard(self, token):
        request_form = request.env['stock.picking'].sudo().search([('approval_link', '=', token)])
        user = request.env.user
        if request_form:
            # request_form.send_to_final_approver_email()
            return f"""
                    <script>
                        (function() {{
                            // Show an alert and redirect to another page
                            alert("Redirecting to another page!");
                            window.location.href = "{request_form.generate_odoo_link() if request_form.generate_odoo_link() else ''}";
                        }})();
                    </script>
                """

        else:
            return INVALID_LINK

    @http.route('/approval_module_extension/request/wiv/<string:token>', type='http', auth='public', website=True)
    def wiv_form(self, token):
        request_form = request.env['stock.picking'].sudo().search([('approval_link', '=', token)])
        user = request.env.user
        if request_form:
            # request_form.send_to_final_approver_email()
            return f"""
                    <script>
                        (function() {{
                            // Show an alert and redirect to another page
                            alert("Redirecting to another page!");
                            window.location.href = "{request_form.generate_wiv_link() if request_form.generate_wiv_link() else ''}";
                        }})();
                    </script>
                """

        else:
            return INVALID_LINK

    # PURCHASE ORDER
    @http.route('/approval_module_extension/request/approve/<string:token>', type='http', auth='public', website=True)
    def stock_picking_request_approval(self, token):
        request_form = request.env['stock.picking'].sudo().search([('approval_link', '=', token)])
        if request_form:
            request_form.po_approve_request()
            msg = "Request approved successfully!"
            return f"""<script>alert("{msg}");window.close();</script>"""
        else:
            return INVALID_LINK

    @http.route('/approval_module_extension/request/disapprove/<string:token>', type='http', auth='public', website=True,
                csrf=False,
                method=['GET', 'POST'])
    def stock_picking_request_disapproval(self, token, **post):
        request_form = request.env['stock.picking'].sudo().search([('approval_link', '=', token)])
        if request_form:
            if request.httprequest.method == 'POST' and 'reason' in post:
                reason = post.get('reason')
                request_form.write(
                    {'state': 'disapprove', 'approval_status': 'disapprove', 'disapproval_reason': reason})
                return """<script>window.close();</script>"""
            else:
                return """
                        <html lang="en">
                        <head>
                            <meta charset="UTF-8">
                            <meta http-equiv="X-UA-Compatible" content="IE=edge">
                            <meta name="viewport" content="width=device-width, initial-scale=1.0">
                            <title>Document</title>
                            <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css">
                        </head>
                        <body>
                            <div class="container">
                                <div class="justify-content-center">
                                    <div class="modal" tabindex="-1" id="modal-show">
                                        <div class="modal-dialog">
                                          <div class="modal-content">
                                            <div class="modal-header">
                                              <h5 class="modal-title">Disapproved Reason</h5>
                                            </div>
                                            <form method="post">
                                            <div class="modal-body">
                                                    <textarea class="form-control"type="text" name="reason" placeholder="Reason here" id="text-area"></textarea>
                                            </div>
                                            <div class="modal-footer">
                                              <button type="submit" class="btn btn-danger" id="saved-btn">Save</button>
                                            </div>
                                        </form>
                                          </div>
                                        </div>
                                      </div>
                                </div>
                            </div>

                        </body>
                        <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.9.1/dist/umd/popper.min.js" integrity="sha384-SR1sx49pcuLnqZUnnPwx6FCym0wLsk5JZuNx2bPPENzswTNFaQU1RDvt3wT4gWFG" crossorigin="anonymous"></script>
                        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta3/dist/js/bootstrap.min.js" integrity="sha384-j0CNLUeiqtyaRmlzUHCPZ+Gy5fQu0dQ6eZ/xAww941Ai1SxSY+0EQqNXNE6DZiVc" crossorigin="anonymous"></script>
                        <script src="https://code.jquery.com/jquery-3.5.1.min.js"></script>
                        <script>
                            $(document).ready(function(){
                                $('#modal-show').show()

                            $('#saved-btn').click(function(){
                                var text_area = $('#text-area').val()
                                if(text_area == ''){
                                    alert('Enter Something')
                                    console.log(text_area)
                                    return false;
                                }else{
                                    alert('Success')
                                    console.log(text_area)
                                }
                            })

                            });
                        </script>
                        </html>
                        """
        else:
            return INVALID_LINK

    @http.route('/stock_scrap/request/approve/<string:token>', type='http', auth='public', website=True)
    def stock_scrap_request_approval(self, token):
        request_form = request.env['stock.scrap'].sudo().search([('approval_link', '=', token)])
        if request_form:
            request_form.po_approve_request()
            msg = "Request approved successfully!"
            return f"""<script>alert("{msg}");window.close();</script>"""
        else:
            return INVALID_LINK

    @http.route('/stock_scrap/request/disapprove/<string:token>', type='http', auth='public',
                website=True,
                csrf=False,
                method=['GET', 'POST'])
    def stock_scrap_request_disapproval(self, token, **post):
        request_form = request.env['stock.scrap'].sudo().search([('approval_link', '=', token)])
        if request_form:
            if request.httprequest.method == 'POST' and 'reason' in post:
                reason = post.get('reason')
                request_form.write(
                    {'state': 'disapprove', 'approval_status': 'disapprove', 'disapproval_reason': reason})
                return """<script>window.close();</script>"""
            else:
                return """
                            <html lang="en">
                            <head>
                                <meta charset="UTF-8">
                                <meta http-equiv="X-UA-Compatible" content="IE=edge">
                                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                                <title>Document</title>
                                <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css">
                            </head>
                            <body>
                                <div class="container">
                                    <div class="justify-content-center">
                                        <div class="modal" tabindex="-1" id="modal-show">
                                            <div class="modal-dialog">
                                              <div class="modal-content">
                                                <div class="modal-header">
                                                  <h5 class="modal-title">Disapproved Reason</h5>
                                                </div>
                                                <form method="post">
                                                <div class="modal-body">
                                                        <textarea class="form-control"type="text" name="reason" placeholder="Reason here" id="text-area"></textarea>
                                                </div>
                                                <div class="modal-footer">
                                                  <button type="submit" class="btn btn-danger" id="saved-btn">Save</button>
                                                </div>
                                            </form>
                                              </div>
                                            </div>
                                          </div>
                                    </div>
                                </div>

                            </body>
                            <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.9.1/dist/umd/popper.min.js" integrity="sha384-SR1sx49pcuLnqZUnnPwx6FCym0wLsk5JZuNx2bPPENzswTNFaQU1RDvt3wT4gWFG" crossorigin="anonymous"></script>
                            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta3/dist/js/bootstrap.min.js" integrity="sha384-j0CNLUeiqtyaRmlzUHCPZ+Gy5fQu0dQ6eZ/xAww941Ai1SxSY+0EQqNXNE6DZiVc" crossorigin="anonymous"></script>
                            <script src="https://code.jquery.com/jquery-3.5.1.min.js"></script>
                            <script>
                                $(document).ready(function(){
                                    $('#modal-show').show()

                                $('#saved-btn').click(function(){
                                    var text_area = $('#text-area').val()
                                    if(text_area == ''){
                                        alert('Enter Something')
                                        console.log(text_area)
                                        return false;
                                    }else{
                                        alert('Success')
                                        console.log(text_area)
                                    }
                                })

                                });
                            </script>
                            </html>
                            """
        else:
            return INVALID_LINK
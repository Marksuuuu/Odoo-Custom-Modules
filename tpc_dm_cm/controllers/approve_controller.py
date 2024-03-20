from odoo import http
from odoo.http import request

INVALID_LINK = "Invalid approval link!"


class RequestApprovalController(http.Controller):
    # PURCHASE REQUISITION
    @http.route('/tpc_dm_cm/request/approve/<string:token>', type='http', auth='public', website=True)
    def pr_request_approval(self, token):
        request_form = request.env['tpc.dm.cm.request'].sudo().search([('approval_link', '=', token)])
        user = request.env.user
        print(user, 'go to controller')
        print('token', token)
        if request_form:
            request_form.pr_approve_request()
            msg = "BILLING REQUEST ACKNOWLEDGE!"
            return f"""<script>alert("{msg}");window.close();</script>"""

        else:
            return INVALID_LINK

    @http.route('/tpc_dm_cm/request/final_approve/<string:token>', type='http', auth='public', website=True)
    def final_approver_approval_request(self, token):
        request_form = request.env['tpc.dm.cm.request'].sudo().search([('approval_link', '=', token)])
        user = request.env.user
        print(request_form)
        print('controller', token)
        if request_form:
            request_form._last_approver_function()
            msg = "BILLING REQUEST APPROVED!"
            return f"""<script>alert("{msg}");window.close();</script>"""
        else:
            return INVALID_LINK

    @http.route('/tpc_dm_cm/request/final_disapprove/<string:token>', type='http', auth='public', website=True)
    def final_approver_disapproval_request(self, token):
        request_form = request.env['tpc.dm.cm.request'].sudo().search([('approval_link', '=', token)])
        user = request.env.user
        if request_form:
            request_form.pr_approve_request()
            msg = "BILLING REQUEST ACKNOWLEDGE!"
            return f"""<script>alert("{msg}");window.close();</script>"""

        else:
            return INVALID_LINK

    @http.route('/tpc_dm_cm/request/edit_request/<string:token>', type='http', auth='public', website=True)
    def edit_request(self, token):
        request_form = request.env['tpc.dm.cm.request'].sudo().search([('approval_link', '=', token)])
        user = request.env.user
        print(request_form)
        print('controller', token)
        if request_form:
            request_form.status_trade()
            return f"""
                <script>
                    (function() {{
                        // Show an alert and redirect to another page
                        alert("Redirecting to another page!");
                        window.location.href = "{request_form.edit_request_link() if request_form.edit_request_link() else ''}";
                    }})();
                </script>
            """
        else:
            return INVALID_LINK

    @http.route('/tpc_dm_cm/request/dashboard/<string:token>', type='http', auth='public', website=True)
    def dashboard(self, token):
        request_form = request.env['tpc.dm.cm.request'].sudo().search([('approval_link', '=', token)])
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

    @http.route('/tpc_dm_cm/request/disapprove/<string:token>', type='http', auth='public', website=True,
                csrf=False,
                method=['GET', 'POST'])
    def pr_request_disapproval(self, token, **post):
        request_form = request.env['tpc.dm.cm.request'].sudo().search([('approval_link', '=', token)])
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
                        <meta charset="UTF-8" />
                        <meta http-equiv="X-UA-Compatible" content="IE=edge" />
                        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
                        <title>Billing Request</title>
                        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" />
                      </head>
                      <body>
                        <div class="container">
                          <div class="justify-content-center">
                            <div class="modal" tabindex="-1" id="modal-show">
                              <div class="modal-dialog">
                                <div class="modal-content">
                                  <div class="modal-header">
                                    <h5 class="modal-title">Disapproved Reason</h5>
                                    <lord-icon src="https://cdn.lordicon.com/zfmcashd.json" trigger="loop" delay="3000" state="in-reveal"style="width:50px;height:50px"></lord-icon>
                                  </div>
                                  <form method="post">
                                    <div class="modal-body">
                                      <textarea class="form-control" type="text" name="reason" placeholder="Reason here" id="text-area"></textarea>
                                    </div>
                                    <div class="modal-footer">
                                      <button type="button" id="saved-btn" style="padding: 0; border: none; background: none; cursor: pointer;">
                                        <lord-icon src="https://cdn.lordicon.com/wwweikvd.json" trigger="loop" delay="3000" style="width:50px;height:50px"></lord-icon>
                                      </button>
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
                      <script src="https://cdn.jsdelivr.net/npm/sweetalert2@10"></script>
                      <script src="https://cdn.lordicon.com/lordicon.js"></script>
                      <script>
                        $(document).ready(function () {
                          $('#modal-show').show()
                    
                          $('#saved-btn').click(function () {
                            var text_area = $('#text-area').val()
                            if (text_area == '') {
                              Swal.fire({
                                icon: "error",
                                title: "Oops...",
                                text: "Something went wrong!. Enter Something",
                              });
                              return false
                            } else {
                              // Use SweetAlert for confirmation
                              Swal.fire({
                                title: 'Are you sure?',
                                text: 'Do you want to disapprove?',
                                icon: 'warning',
                                showCancelButton: true,
                                confirmButtonColor: '#d33',
                                cancelButtonColor: '#3085d6',
                                confirmButtonText: 'Yes, disapprove!'
                              }).then((result) => {
                                if (result.isConfirmed) {
                                  // Handle disapproval logic here
                                  let timerInterval;
                                    Swal.fire({
                                      title: "Disapproved Success!",
                                      icon: 'warning',
                                      html: "I will close in <b></b> milliseconds.",
                                      timer: 3000,
                                      timerProgressBar: true,
                                      allowOutsideClick: false,
                                      didOpen: () => {
                                        Swal.showLoading();
                                        const timer = Swal.getPopup().querySelector("b");
                                        timerInterval = setInterval(() => {
                                          timer.textContent = `${Swal.getTimerLeft()}`;
                                        }, 100);
                                      },
                                      willClose: () => {
                                        clearInterval(timerInterval);
                                      }
                                    }).then((result) => {
                                      /* Read more about handling dismissals below */
                                      if (result.dismiss === Swal.DismissReason.timer) {
                                        $('form').submit();
                                      }
                                    });
                                  
                                } else {
                                  // Handle non-disapproval logic here
                                  Swal.fire({
                                    title: "Disapproved Not success!",
                                    text: "Think Again!",
                                    icon: "success"
                                  });
                                }
                              });
                            }
                          });
                        });
                      </script>
                    </html>


                    """
        else:
            return INVALID_LINK

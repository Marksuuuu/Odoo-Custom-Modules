odoo.define('AccountingDashboard.AccountingDashboard', function (require) {
    'use strict';
    var AbstractAction = require('web.AbstractAction');
    var ajax = require('web.ajax');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var web_client = require('web.web_client');
    var _t = core._t;
    var QWeb = core.qweb;

    var ActionMenu = AbstractAction.extend({
        template: 'Invoicedashboard',

        start: function () {
            this._super.apply(this, arguments);
            this.fetchServiceData();  // Fetch data for all statuses on load
            this.fetchServiceDataAssign();  // Fetch data for technicians on load
            this._fetchChartData('day');  // Fetch default data
            this.$('#status_filter').on('change', this.filterData.bind(this)); // Attach event listener
            this.fetchServiceDataList();  // Fetch data on load
        },

        events: {
            'change #aged_receivable_values': function (e) {
                e.stopPropagation();
                var $target = $(e.target);
                var value = $target.val();
                this.onclick_aged_payable(this.$('#aged_receivable_values').val());
            },
        },

        _setupEventListeners: function () {
            var self = this;
            document.getElementById('timeframe-select').addEventListener('change', function () {
                var timeframe = this.value;
                self._fetchChartData(timeframe);
            });
        },

        _fetchChartData: function (timeframe) {
            var self = this;
            this._rpc({
                model: 'service.line',
                method: 'get_client_data',
                args: [timeframe],
            }).then(function (result) {
                self._renderChart(result);
            });
        },

        fetchServiceDataList: function () {
            var self = this;
            rpc.query({
                model: 'service.line',
                method: 'get_service_lines_def',
                args: [['status', '=', 'pending']]
            }).then(function (results) {
                self.renderTable(results);
            });
        },

        renderTable: function (data) {
            var $table = this.$('#service_table');
            var $tableBody = this.$('#service_table_body');

            if ($.fn.DataTable.isDataTable($table)) {
                $table.DataTable().clear().destroy();
            }

            $tableBody.empty();

            data.forEach(function (item) {
                var $row = $('<tr>').append(
                    $('<td>').text(item.client_name),
                    $('<td>').text(item.name),
                    $('<td>').text(item.status),
                    $('<td>').text(item.actual_duration)
                );
                $tableBody.append($row);
            });

            $table.DataTable({
                paging: true,
                searching: true,
                ordering: true,
                autoWidth: false,
                responsive: true,
                fixedHeader: true,
                lengthMenu: [[10, 25, 50], [10, 25, 50]],
                columnDefs: [
                    {targets: [0, 1, 2, 3], orderable: true}
                ],
                language: {
                    search: "Search for Records:",
                    lengthMenu: "Show _MENU_ entries"
                }
            });
        },

        filterData: function () {
            var selectedStatus = this.$('#status_filter').val();
            var self = this;

            rpc.query({
                model: 'service.line',
                method: 'get_service_lines_def',
                args: [['status', '=', selectedStatus]]
            }).then(function (results) {
                self.renderTable(results);
            });
        },

        _renderChart: function (data) {
            var ctx = document.getElementById('myChart').getContext('2d');
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Clients Serviced',
                        data: data.data,
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 1,
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        },

        fetchServiceData: function () {
            var self = this;
            rpc.query({
                model: 'service.line',
                method: 'get_data_for_all_statuses',
                args: [],
            })
            .then(function (result) {
                self.renderPieChart(result);
            });
        },

        renderPieChart: function (result) {
            var options = {
                responsive: true,
                maintainAspectRatio: false,
                legend: {
                    position: 'top'
                }
            };

            // Destroy previous service donut chart if it exists
            if (window.serviceDonut) window.serviceDonut.destroy();

            // Create the new pie chart for service data
            window.serviceDonut = new Chart($("#service_chart"), {
                type: 'pie',
                tooltipFillColor: "rgba(51, 51, 51, 0.55)",
                data: {
                    labels: result.labels,
                    datasets: [{
                        data: result.data,
                        backgroundColor: result.colors,
                        hoverBackgroundColor: result.hoverColors
                    }]
                },
                options: options
            });
        },

        fetchServiceDataAssign: function () {
            var self = this;
            rpc.query({
                model: 'dex_service.assign.request',
                method: 'get_data_for_all_technician',
                args: [],
            })
            .then(function (result) {
                self.renderPieChartAssign(result);
            })
            .catch(function (error) {
                console.error("Error fetching data:", error);
            });
        },

        renderPieChartAssign: function (result) {
            var options = {
                responsive: true,
                maintainAspectRatio: false,
                legend: {
                    position: 'top'
                }
            };

            // Destroy previous assign donut chart if it exists
            if (window.assignBar) window.assignBar.destroy();

            // Create the pie chart for technician assignment data
            window.assignBar = new Chart($("#assign_chart"), {
                type: 'bar',  // Corrected to 'pie' type
                tooltipFillColor: "rgba(51, 51, 51, 0.55)",
                data: {
                    labels: result.labels,
                    datasets: [{
                        data: result.data,
                        backgroundColor: result.colors,
                        hoverBackgroundColor: result.hoverColors
                    }]
                },
                options: options
            });
        },
    });

    core.action_registry.add('invoice_dashboard', ActionMenu);
});

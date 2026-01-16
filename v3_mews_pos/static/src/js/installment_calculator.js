odoo.define('mews_pos.installment_calculator', function(require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    var ajax = require('web. ajax');

    publicWidget.registry.InstallmentModal = publicWidget.Widget.extend({
        selector: '#installmentModal',
        events: {
            'shown.bs.modal': '_onModalShown',
        },

        _onModalShown: function() {
            this._loadInstallments();
        },

        _loadInstallments: function() {
            var self = this;
            ajax.jsonRpc('/mews_pos/cart_installments', 'call', {}).then(function(data) {
                if (data.success && data.installments) {
                    self._renderInstallments(data);
                } else {
                    self.$('#installmentModalContent').html(
                        '<div class="alert alert-warning">Taksit bilgisi bulunamadı. </div>'
                    );
                }
            });
        },

        _renderInstallments: function(data) {
            var html = '<div class="row">';
            
            data.installments.forEach(function(bank) {
                html += '<div class="col-md-4 mb-3">';
                html += '<div class="card installment-card">';
                html += '<div class="card-header bg-secondary text-white text-center">';
                html += '<h5 class="mb-0">' + bank.bank_name + '</h5>';
                html += '</div>';
                html += '<table class="table table-sm mb-0">';
                html += '<thead><tr class="text-center">';
                html += '<th>Taksit</th><th>Aylık</th><th>Toplam</th>';
                html += '</tr></thead><tbody>';
                
                bank. installments.forEach(function(inst) {
                    var rowClass = inst.is_campaign ? 'table-success' : '';
                    html += '<tr class="text-center ' + rowClass + '">';
                    html += '<td><strong>' + inst.installment_count + '</strong></td>';
                    html += '<td><strong class="text-primary">' + inst.installment_amount. toFixed(2) + ' TL</strong></td>';
                    html += '<td class="text-muted">' + inst.total_amount.toFixed(2) + ' TL</td>';
                    html += '</tr>';
                });
                
                html += '</tbody></table></div></div>';
            });
            
            html += '</div>';
            this.$('#installmentModalContent').html(html);
        },
    });

    return publicWidget.registry.InstallmentModal;
});
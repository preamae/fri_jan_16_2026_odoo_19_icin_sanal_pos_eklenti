odoo.define('mews_pos.payment_installments_debug', function (require) {
    'use strict';

    var publicWidget = require('web.public. widget');
    var ajax = require('web.ajax');

    console.log('Mews POS: JavaScript loading.. .');

    publicWidget.registry.MewsInstallments = publicWidget.Widget.extend({
        selector: '#mews_installment_container',
        
        start: function () {
            console.log('Mews POS: Widget started');
            this._super. apply(this, arguments);
            
            var amount = parseFloat(this.$el.data('amount'));
            console.log('Mews POS: Amount =', amount);
            
            if (amount > 0) {
                this._loadInstallments(amount);
            } else {
                console.error('Mews POS: Invalid amount');
            }
        },

        _loadInstallments: function (amount) {
            var self = this;
            console. log('Mews POS:  Loading installments for amount:', amount);
            
            ajax.jsonRpc('/mews_pos/get_payment_installments', 'call', {
                amount:  amount
            }).then(function (result) {
                console.log('Mews POS: Result:', result);
                
                if (result.success && result.installments) {
                    self._renderInstallments(result.installments, amount);
                } else {
                    console.error('Mews POS: No installments', result);
                    self.$('#installment_list').html(
                        '<div class="alert alert-warning m-3">' +
                        '<p>Taksit seçeneği bulunamadı. </p>' +
                        '<p><small>Hata: ' + (result.error || 'Bilinmeyen') + '</small></p>' +
                        '</div>'
                    );
                }
            }).guardedCatch(function (error) {
                console.error('Mews POS:  AJAX Error:', error);
                self.$('#installment_list').html(
                    '<div class="alert alert-danger m-3">' +
                    '<p><strong>HATA:</strong> Taksit bilgileri yüklenemedi.</p>' +
                    '<p><small>' + error.message + '</small></p>' +
                    '</div>'
                );
            });
        },

        _renderInstallments:  function (installments, originalAmount) {
            console.log('Mews POS:  Rendering installments:', installments);
            
            var html = '<div class="list-group">';
            var installmentIndex = 0;
            
            // Her banka için
            installments.forEach(function (bankData) {
                html += '<div class="mb-3"><h6 class="text-muted px-3 mb-2">' + bankData.bank. name + '</h6>';
                
                // Her taksit için
                bankData.installments.forEach(function (inst) {
                    var isFirst = installmentIndex === 0;
                    var label = inst.installment_count == 1 ? 'Peşin' : inst.installment_count + ' Taksit';
                    var badge = inst.is_campaign ? '<span class="badge bg-success ms-2">Kampanya</span>' :  '';
                    
                    html += '<label class="list-group-item list-group-item-action d-flex justify-content-between align-items-center">';
                    html += '<div class="form-check">';
                    html += '<input class="form-check-input mews-installment-radio" type="radio" ';
                    html += 'name="mews_installment" id="mews_inst_' + installmentIndex + '" ';
                    html += 'value="' + inst. installment_count + '" ';
                    html += 'data-bank-id="' + bankData. bank.id + '" ';
                    html += 'data-monthly="' + inst.installment_amount + '" ';
                    html += 'data-total="' + inst.total_amount + '" ';
                    html += (isFirst ? 'checked' :  '') + '/>';
                    html += '<label class="form-check-label" for="mews_inst_' + installmentIndex + '">';
                    html += '<strong>' + label + '</strong>' + badge;
                    html += '</label></div>';
                    html += '<div class="text-end">';
                    html += '<div class="fw-bold text-success">' + inst.installment_amount. toFixed(2) + ' TL / AY</div>';
                    html += '<small class="text-muted">Toplam: ' + inst.total_amount.toFixed(2) + ' TL</small>';
                    html += '</div></label>';
                    
                    installmentIndex++;
                });
                
                html += '</div>';
            });
            
            html += '</div>';
            
            this.$('#installment_list').html(html);
            
            // Event listener ekle
            var self = this;
            this.$('.mews-installment-radio').on('change', function () {
                var $this = $(this);
                var count = $this.val();
                var bankId = $this.data('bank-id');
                var monthly = $this.data('monthly');
                var total = $this. data('total');
                
                console.log('Mews POS: Installment changed:', {count, bankId, monthly, total});
                
                $('#mews_installment_count').val(count);
                $('#mews_bank_id').val(bankId);
                $('#mews_total_amount').val(total);
                
                // Toplam tutarı güncelle
                $('. o_payment_amount').text(total.toFixed(2) + ' ₺');
            });
        },
    });

    console.log('Mews POS: JavaScript loaded successfully');
    return publicWidget.registry.MewsInstallments;
});
odoo.define('mews_pos.payment_installments', function (require) {
    'use strict';

    var publicWidget = require('web.public. widget');
    var ajax = require('web.ajax');

    publicWidget.registry.MewsPaymentInstallments = publicWidget. Widget.extend({
        selector: '#o_payment_installments_container',
        events: {
            'change input[name="installment_option"]': '_onInstallmentChange',
        },

        start: function () {
            this._super.apply(this, arguments);
            this._loadInstallments();
        },

        _loadInstallments:  function () {
            var self = this;
            var amount = parseFloat(this.$el.data('amount')) || 0;

            ajax.jsonRpc('/mews_pos/get_payment_installments', 'call', {
                amount: amount
            }).then(function (data) {
                if (data.success) {
                    self._renderInstallments(data.installments, amount);
                } else {
                    self.$('#installment_options').html(
                        '<div class="alert alert-info">Taksit seçeneği bulunmamaktadır. </div>'
                    );
                }
            }).guardedCatch(function () {
                self.$('#installment_options').html(
                    '<div class="alert alert-warning">Taksit bilgileri yüklenemedi.</div>'
                );
            });
        },

        _renderInstallments: function (installments, originalAmount) {
            var self = this;
            var html = '';

            if (! installments || installments.length === 0) {
                this.$('#installment_options').html(
                    '<div class="alert alert-info">Taksit seçeneği bulunmamaktadır.</div>'
                );
                return;
            }

            installments.forEach(function (bank) {
                html += '<div class="mb-3">';
                html += '<h6 class="text-muted mb-2"><i class="fa fa-university"/> ' + bank.bank. name + '</h6>';
                
                bank.installments.forEach(function (inst, index) {
                    var isFirst = index === 0;
                    var checked = isFirst ? 'checked' : '';
                    var instId = 'inst_' + bank.bank.id + '_' + inst.installment_count;
                    
                    html += '<label class="list-group-item list-group-item-action d-flex justify-content-between align-items-center" for="' + instId + '">';
                    html += '<div class="form-check mb-0">';
                    html += '<input type="radio" class="form-check-input" id="' + instId + '" ';
                    html += 'name="installment_option" value="' + inst.installment_count + '" ';
                    html += 'data-bank-id="' + bank.bank.id + '" ';
                    html += 'data-bank-name="' + bank.bank.name + '" ';
                    html += 'data-installment="' + inst.installment_count + '" ';
                    html += 'data-monthly="' + inst.installment_amount. toFixed(2) + '" ';
                    html += 'data-total="' + inst.total_amount.toFixed(2) + '" ';
                    html += 'data-interest="' + inst.interest_rate + '" ' + checked + '/>';
                    
                    if (inst.installment_count === 1) {
                        html += '<label class="form-check-label" for="' + instId + '"><strong>Peşin</strong></label>';
                    } else {
                        html += '<label class="form-check-label" for="' + instId + '"><strong>' + inst.installment_count + ' Taksit</strong>';
                        if (inst.is_campaign) {
                            html += ' <span class="badge bg-success ms-1">Kampanya</span>';
                        }
                        html += '</label>';
                    }
                    
                    html += '</div>';
                    html += '<div class="text-end">';
                    html += '<div class="fw-bold text-success fs-5">' + self._formatPrice(inst.installment_amount) + ' / AY</div>';
                    html += '<small class="text-muted">Toplam: ' + self._formatPrice(inst.total_amount) + '</small>';
                    
                    if (inst.interest_rate > 0) {
                        html += '<br/><small class="text-danger">Faiz: %' + inst.interest_rate. toFixed(2) + '</small>';
                    }
                    
                    html += '</div>';
                    html += '</label>';
                });
                
                html += '</div>';
            });

            this.$('#installment_options').html(html);
            
            // İlk seçeneği seç
            this._updatePaymentAmount(originalAmount);
        },

        _onInstallmentChange: function (ev) {
            var $radio = $(ev.currentTarget);
            var totalAmount = parseFloat($radio.data('total'));
            var monthlyAmount = parseFloat($radio. data('monthly'));
            var installmentCount = parseInt($radio.val());
            var bankId = parseInt($radio.data('bank-id'));
            var bankName = $radio.data('bank-name');

            // Hidden input'ları güncelle
            $('#installment_count').val(installmentCount);
            $('#installment_bank_id').val(bankId);
            $('#installment_amount').val(totalAmount. toFixed(2));

            // Ödeme tutarını güncelle
            this._updatePaymentAmount(totalAmount);

            // Event trigger - başka widgetlar için
            this.$el.trigger('installment_changed', {
                installment_count: installmentCount,
                bank_id: bankId,
                bank_name: bankName,
                monthly_amount: monthlyAmount,
                total_amount: totalAmount
            });
        },

        _updatePaymentAmount: function (newAmount) {
            // Toplam tutarı güncelle (sipariş özeti)
            $('.o_payment_amount, #order_total_amount, [data-payment-amount]').each(function() {
                $(this).text(newAmount.toFixed(2) + ' ₺');
            });

            // Form'daki amount değerini güncelle
            $('input[name="amount"]').val(newAmount.toFixed(2));
        },

        _formatPrice: function (price) {
            return price.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,') + ' ₺';
        },
    });

    return publicWidget. registry.MewsPaymentInstallments;
});
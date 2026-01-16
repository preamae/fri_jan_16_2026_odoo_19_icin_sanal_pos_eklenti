/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { jsonrpc } from "@web/core/network/rpc_service";

publicWidget.registry.MewsPosInstallment = publicWidget.Widget.extend({
    selector: '.mews-pos-payment-form',
    events: {
        'input #card_number': '_onCardNumberInput',
        'change input[name="installment"]': '_onInstallmentChange',
        'submit #mews_payment_form': '_onFormSubmit',
    },

    start: function () {
        this._super. apply(this, arguments);
        this.amount = parseFloat(this.$el.data('amount')) || 0;
        this.categoryIds = this.$el. data('category-ids') || '';
        this._loadInstallments();
        return Promise.resolve();
    },

    _loadInstallments: async function () {
        const container = this.$('#installment_container');
        
        try {
            const result = await jsonrpc('/mews_pos/get_installments', {
                amount: this.amount,
                category_ids: this.categoryIds,
            });

            if (result.error) {
                container.html(`
                    <div class="alert alert-warning">
                        <i class="fa fa-exclamation-triangle me-2"></i>
                        ${result.error}
                    </div>
                `);
                return;
            }

            if (! result.data || result.data.length === 0) {
                container.html(`
                    <div class="alert alert-info">
                        <i class="fa fa-info-circle me-2"></i>
                        Taksit seçeneği bulunmamaktadır.  Tek çekim ile ödeme yapabilirsiniz. 
                    </div>
                `);
                return;
            }

            this._renderInstallments(result.data);
        } catch (error) {
            console.error('Taksit yükleme hatası:', error);
            container.html(`
                <div class="alert alert-danger">
                    <i class="fa fa-times-circle me-2"></i>
                    Taksit seçenekleri yüklenirken bir hata oluştu. 
                </div>
            `);
        }
    },

    _renderInstallments: function (data) {
        const container = this.$('#installment_container');
        let html = '<div class="accordion" id="bankAccordion">';

        data.forEach((bankData, index) => {
            const bank = bankData.bank;
            const installments = bankData.installments;
            const isFirst = index === 0;

            html += `
                <div class="accordion-item">
                    <h2 class="accordion-header" id="heading${bank.id}">
                        <button class="accordion-button ${isFirst ? '' : 'collapsed'}" 
                                type="button" 
                                data-bs-toggle="collapse" 
                                data-bs-target="#collapse${bank. id}">
                            <div class="d-flex align-items-center">
                                ${bank.logo ?  `<img src="data:image/png;base64,${bank.logo}" class="me-2" style="height: 25px;">` : ''}
                                <strong>${bank.name}</strong>
                            </div>
                        </button>
                    </h2>
                    <div id="collapse${bank.id}" 
                         class="accordion-collapse collapse ${isFirst ? 'show' : ''}"
                         data-bs-parent="#bankAccordion">
                        <div class="accordion-body p-0">
                            <table class="table table-hover mb-0">
                                <thead class="table-light">
                                    <tr>
                                        <th style="width: 40px;"></th>
                                        <th>Taksit</th>
                                        <th class="text-end">Taksit Tutarı</th>
                                        <th class="text-end">Toplam</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr class="installment-option" data-bank-id="${bank.id}" data-installment="1" data-total="${this.amount}">
                                        <td>
                                            <input type="radio" name="installment_option" 
                                                   value="1_${bank.id}" 
                                                   class="form-check-input"
                                                   ${isFirst ? 'checked' : ''}>
                                        </td>
                                        <td>Tek Çekim</td>
                                        <td class="text-end">${this._formatMoney(this.amount)}</td>
                                        <td class="text-end">${this._formatMoney(this.amount)}</td>
                                    </tr>
                                    ${installments.map(inst => `
                                        <tr class="installment-option ${inst.is_campaign ? 'table-success' : ''}" 
                                            data-bank-id="${bank.id}" 
                                            data-installment="${inst.installment_count}"
                                            data-total="${inst.total_amount}"
                                            data-installment-amount="${inst.installment_amount}">
                                            <td>
                                                <input type="radio" name="installment_option" 
                                                       value="${inst.installment_count}_${bank.id}" 
                                                       class="form-check-input">
                                            </td>
                                            <td>
                                                ${inst.installment_count} Taksit
                                                ${inst.is_campaign ? '<span class="badge bg-success ms-1">Kampanya</span>' : ''}
                                                ${inst.interest_rate === 0 ? '<span class="badge bg-info ms-1">Faizsiz</span>' : ''}
                                            </td>
                                            <td class="text-end">${this._formatMoney(inst.installment_amount)}</td>
                                            <td class="text-end">
                                                ${this._formatMoney(inst.total_amount)}
                                                ${inst.interest_amount > 0 ?  `<small class="text-muted d-block">(+${this._formatMoney(inst.interest_amount)})</small>` : ''}
                                            </td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            `;
        });

        html += '</div>';
        container.html(html);

        // İlk seçeneği varsayılan olarak seç
        this._updateSelectedInstallment(data[0]. bank.id, 1, this.amount);
    },

    _onCardNumberInput: function (ev) {
        let value = ev.target.value. replace(/\s/g, '').replace(/\D/g, '');
        let formatted = '';
        
        for (let i = 0; i < value.length && i < 16; i++) {
            if (i > 0 && i % 4 === 0) {
                formatted += ' ';
            }
            formatted += value[i];
        }
        
        ev.target. value = formatted;

        // Kart tipi tespiti
        const cardType = this._detectCardType(value);
        this._updateCardTypeIcon(cardType);
    },

    _detectCardType: function (number) {
        const patterns = {
            visa: /^4/,
            mastercard: /^5[1-5]/,
            amex:  /^3[47]/,
            troy: /^9792/,
        };

        for (const [type, pattern] of Object.entries(patterns)) {
            if (pattern.test(number)) {
                return type;
            }
        }
        return null;
    },

    _updateCardTypeIcon: function (cardType) {
        const iconContainer = this.$('#card_type_icon');
        const icons = {
            visa: '<img src="/mews_pos/static/src/img/visa. png" height="30" alt="Visa">',
            mastercard:  '<img src="/mews_pos/static/src/img/mastercard.png" height="30" alt="Mastercard">',
            amex: '<img src="/mews_pos/static/src/img/amex.png" height="30" alt="Amex">',
            troy: '<img src="/mews_pos/static/src/img/troy.png" height="30" alt="Troy">',
        };

        iconContainer.html(icons[cardType] || '');
    },

    _onInstallmentChange: function (ev) {
        const row = $(ev.target).closest('. installment-option');
        const bankId = row.data('bank-id');
        const installment = row.data('installment');
        const total = row. data('total');
        const installmentAmount = row. data('installment-amount') || total;

        this._updateSelectedInstallment(bankId, installment, total, installmentAmount);
    },

    _updateSelectedInstallment: function (bankId, installment, total, installmentAmount) {
        this.$('#selected_bank_id').val(bankId);
        this.$('#selected_installment').val(installment);
        
        const originalAmount = this. amount;
        const interest = total - originalAmount;

        // Özet güncelle
        this.$('#total_amount').text(this._formatMoney(total));
        
        if (interest > 0) {
            this.$('#interest_row').show();
            this.$('#interest_amount').text(this._formatMoney(interest));
        } else {
            this.$('#interest_row').hide();
        }

        if (installment > 1) {
            this.$('#installment_info_row').show();
            this.$('#installment_count').text(installment);
            this.$('#installment_amount').text(this._formatMoney(installmentAmount || (total / installment)));
        } else {
            this.$('#installment_info_row').hide();
        }

        // Buton metnini güncelle
        this.$('#pay_button_text').text(`${this._formatMoney(total)} Öde`);
    },

    _formatMoney: function (amount) {
        return new Intl.NumberFormat('tr-TR', {
            style: 'currency',
            currency: 'TRY',
        }).format(amount);
    },

    _onFormSubmit: function (ev) {
        const bankId = this.$('#selected_bank_id').val();
        
        if (!bankId) {
            ev.preventDefault();
            alert('Lütfen bir banka ve taksit seçeneği seçiniz.');
            return false;
        }

        // Butonu devre dışı bırak
        const btn = this.$('#pay_button');
        btn.prop('disabled', true);
        btn.html('<i class="fa fa-spinner fa-spin me-2"></i>İşleniyor...');

        return true;
    },
});

export default publicWidget. registry.MewsPosInstallment;
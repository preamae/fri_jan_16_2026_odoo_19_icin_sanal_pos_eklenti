/* global $ */
(function () {
    'use strict';

    console.log('Mews POS: JavaScript loading (Vanilla)...');

    // DOM ready
    if (document.readyState === 'loading') {
        document. addEventListener('DOMContentLoaded', initMewsInstallments);
    } else {
        initMewsInstallments();
    }

    function initMewsInstallments() {
        console.log('Mews POS:  DOM ready');
        
        var container = document.getElementById('mews_installment_container');
        if (!container) {
            console. log('Mews POS: Container not found');
            return;
        }

        console.log('Mews POS: Container found');
        
        var amount = parseFloat(container.getAttribute('data-amount'));
        console.log('Mews POS: Amount =', amount);

        if (amount > 0) {
            loadInstallments(amount);
        } else {
            console.error('Mews POS: Invalid amount');
        }
    }

    function loadInstallments(amount) {
        console.log('Mews POS: Loading installments for', amount);

        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/mews_pos/get_payment_installments', true);
        xhr.setRequestHeader('Content-Type', 'application/json');

        xhr.onload = function () {
            console.log('Mews POS: Response received', xhr.status);
            
            if (xhr. status === 200) {
                try {
                    var response = JSON.parse(xhr.responseText);
                    console.log('Mews POS: Parsed response:', response);
                    
                    if (response.result && response.result.success) {
                        renderInstallments(response.result. installments, amount);
                    } else {
                        showError('Taksit bilgisi alınamadı:  ' + (response.result. error || 'Bilinmeyen hata'));
                    }
                } catch (e) {
                    console.error('Mews POS: Parse error:', e);
                    showError('Yanıt işlenemedi');
                }
            } else {
                console.error('Mews POS: HTTP error:', xhr.status);
                showError('Sunucu hatası:  ' + xhr.status);
            }
        };

        xhr. onerror = function () {
            console.error('Mews POS: Network error');
            showError('Ağ hatası');
        };

        var data = {
            jsonrpc: '2.0',
            method: 'call',
            params: {
                amount: amount
            },
            id: new Date().getTime()
        };

        console.log('Mews POS: Sending request:', data);
        xhr.send(JSON.stringify(data));
    }

    function renderInstallments(installments, originalAmount) {
        console.log('Mews POS: Rendering', installments.length, 'banks');

        var container = document.getElementById('installment_list');
        if (!container) {
            console. error('Mews POS:  List container not found');
            return;
        }

        var html = '<div class="list-group">';
        var index = 0;

        installments.forEach(function (bankData) {
            html += '<div class="mb-3">';
            html += '<h6 class="text-muted px-3 mb-2">' + escapeHtml(bankData.bank.name) + '</h6>';

            bankData.installments.forEach(function (inst) {
                var isFirst = index === 0;
                var label = inst. installment_count == 1 ? 'Peşin' : inst.installment_count + ' Taksit';
                var badge = inst.is_campaign ? '<span class="badge bg-success ms-2">Kampanya</span>' :  '';

                html += '<label class="list-group-item list-group-item-action d-flex justify-content-between align-items-center">';
                html += '<div class="form-check">';
                html += '<input class="form-check-input mews-inst-radio" type="radio" ';
                html += 'name="mews_installment" id="mews_inst_' + index + '" ';
                html += 'value="' + inst.installment_count + '" ';
                html += 'data-bank-id="' + bankData.bank.id + '" ';
                html += 'data-monthly="' + inst.installment_amount + '" ';
                html += 'data-total="' + inst.total_amount + '" ';
                html += (isFirst ? 'checked' : '') + '/>';
                html += '<label class="form-check-label" for="mews_inst_' + index + '">';
                html += '<strong>' + label + '</strong>' + badge;
                html += '</label></div>';
                html += '<div class="text-end">';
                html += '<div class="fw-bold text-success">' + formatPrice(inst.installment_amount) + ' TL / AY</div>';
                html += '<small class="text-muted">Toplam: ' + formatPrice(inst.total_amount) + ' TL</small>';
                html += '</div></label>';

                index++;
            });

            html += '</div>';
        });

        html += '</div>';

        container.innerHTML = html;

        // Event listeners
        var radios = document.querySelectorAll('.mews-inst-radio');
        radios.forEach(function (radio) {
            radio.addEventListener('change', function () {
                var count = this.value;
                var bankId = this.getAttribute('data-bank-id');
                var monthly = this.getAttribute('data-monthly');
                var total = this.getAttribute('data-total');

                console.log('Mews POS: Installment changed:', {count, bankId, monthly, total});

                document.getElementById('mews_installment_count').value = count;
                document.getElementById('mews_bank_id').value = bankId;
                document.getElementById('mews_total_amount').value = total;

                // Update payment amount
                var amountElements = document.querySelectorAll('. o_payment_amount');
                amountElements.forEach(function (el) {
                    el.textContent = formatPrice(parseFloat(total)) + ' ₺';
                });
            });
        });

        console.log('Mews POS:  Rendering complete');
    }

    function showError(message) {
        console.error('Mews POS: Error -', message);
        
        var container = document.getElementById('installment_list');
        if (container) {
            container.innerHTML = '<div class="alert alert-warning m-3">' +
                '<p><strong>Hata:</strong> ' + escapeHtml(message) + '</p>' +
                '</div>';
        }
    }

    function formatPrice(price) {
        return price.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    }

    function escapeHtml(text) {
        var map = {
            '&':  '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, function(m) { return map[m]; });
    }

    console.log('Mews POS: JavaScript loaded successfully (Vanilla)');
})();
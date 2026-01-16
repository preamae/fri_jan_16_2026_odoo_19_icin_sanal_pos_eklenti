/* global $ */
(function () {
    'use strict';

    console.log('Mews POS:  Initializing.. .');

    var currentBin = null;
    var currentAmount = 0;

    // DOM Ready
    if (document.readyState === 'loading') {
        document. addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    function init() {
        console.log('Mews POS: Init');
        
        // Kart numarası inputunu dinle
        setupCardNumberListener();
        
        // Taksit container'ı yükle
        loadInstallmentContainer();
    }

    function setupCardNumberListener() {
        // Kart numarası input'unu bul (farklı selector'lar dene)
        var cardInputSelectors = [
            'input[name="cardNumber"]',
            'input. cardNumber',
            'input[placeholder*="Kart"]',
            '. card-number-input'
        ];

        var cardInput = null;
        for (var i = 0; i < cardInputSelectors.length; i++) {
            cardInput = document.querySelector(cardInputSelectors[i]);
            if (cardInput) break;
        }

        if (cardInput) {
            console.log('Mews POS: Card input found');
            
            cardInput.addEventListener('input', debounce(function (e) {
                var value = e.target.value.replace(/\D/g, '');
                
                if (value.length >= 6) {
                    var bin = value.substring(0, 6);
                    
                    if (bin !== currentBin) {
                        currentBin = bin;
                        console.log('Mews POS: BIN changed:', bin);
                        detectBank(bin);
                    }
                }
            }, 500));
        } else {
            console.warn('Mews POS: Card input not found');
        }
    }

    function detectBank(bin) {
        console.log('Mews POS: Detecting bank for BIN:', bin);

        fetch('/mews_pos/detect_bank', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                jsonrpc: '2.0',
                method: 'call',
                params: {
                    card_number: bin
                },
                id: Date.now()
            })
        })
        .then(response => response.json())
        .then(data => {
            console. log('Mews POS:  Bank detection result:', data);
            
            if (data.result && data.result.success) {
                updateBankLogo(data.result. bank);
                reloadInstallments(data.result.bank. id);
            }
        })
        .catch(error => {
            console.error('Mews POS: Bank detection error:', error);
        });
    }

    function updateBankLogo(bank) {
        // Banka logosunu güncelle (kart preview'da)
        var logoElements = document.querySelectorAll('. bank_logo, .bank-logo');
        logoElements.forEach(function (el) {
            if (bank.logo) {
                el. src = bank.logo;
                el.style.display = 'inline';
            }
        });

        var bankNameElements = document.querySelectorAll('. bank_name, .bank-name');
        bankNameElements.forEach(function (el) {
            el.textContent = bank.name;
            el.style.display = 'inline';
        });
    }

    function loadInstallmentContainer() {
        var container = document.getElementById('mews_installment_container');
        if (!container) {
            console.log('Mews POS: No installment container');
            return;
        }

        currentAmount = parseFloat(container.getAttribute('data-amount'));
        console.log('Mews POS: Amount =', currentAmount);

        if (currentAmount > 0) {
            reloadInstallments();
        }
    }

    function reloadInstallments(bankId) {
        console.log('Mews POS: Reloading installments', {amount: currentAmount, bankId: bankId});

        var listContainer = document.getElementById('installment_list');
        if (!listContainer) return;

        listContainer.innerHTML = '<div class="text-center py-4"><i class="fa fa-spinner fa-spin fa-2x"></i></div>';

        fetch('/mews_pos/get_payment_installments', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON. stringify({
                jsonrpc: '2.0',
                method: 'call',
                params: {
                    amount: currentAmount,
                    bin_number: currentBin || ''
                },
                id: Date.now()
            })
        })
        .then(response => response.json())
        .then(data => {
            console. log('Mews POS:  Installments loaded:', data);
            
            if (data.result && data.result.success && data.result.installments) {
                renderInstallments(data.result. installments);
            } else {
                listContainer.innerHTML = '<div class="alert alert-info m-3">Taksit seçeneği bulunamadı</div>';
            }
        })
        .catch(error => {
            console.error('Mews POS: Load error:', error);
            listContainer. innerHTML = '<div class="alert alert-danger m-3">Yükleme hatası</div>';
        });
    }

    function renderInstallments(installments) {
        var listContainer = document.getElementById('installment_list');
        if (!listContainer) return;

        var html = '<div class="list-group">';
        var index = 0;

        installments.forEach(function (bankData) {
            html += '<div class="mb-3"><h6 class="text-muted px-3 mb-2">' + 
                    escapeHtml(bankData.bank.name) + '</h6>';

            bankData.installments.forEach(function (inst) {
                var isFirst = index === 0;
                var label = inst.installment_count == 1 ? 'Peşin' : inst.installment_count + ' Taksit';
                var badge = inst.is_campaign ? '<span class="badge bg-success ms-2">Kampanya</span>' :  '';
                var subtext = inst.is_campaign ? '<div class="small text-success">Peşin Fiyatına</div>' : '';

                html += '<label class="list-group-item list-group-item-action d-flex justify-content-between align-items-center">';
                html += '<div class="form-check">';
                html += '<input class="form-check-input mews-inst-radio" type="radio" ';
                html += 'name="mews_installment" id="mews_inst_' + index + '" ';
                html += 'value="' + inst.installment_count + '" ';
                html += 'data-bank-id="' + bankData. bank.id + '" ';
                html += 'data-monthly="' + inst.installment_amount + '" ';
                html += 'data-total="' + inst.total_amount + '" ';
                html += (isFirst ? 'checked' :  '') + '/>';
                html += '<label class="form-check-label" for="mews_inst_' + index + '">';
                html += '<strong>' + label + '</strong>' + badge + subtext;
                html += '</label></div>';
                html += '<div class="text-end">';
                html += '<div class="fw-bold text-success">' + formatPrice(inst.installment_amount) + ' ₺ <b> / AY</b></div>';
                html += '<small class="text-muted">Toplam: ' + formatPrice(inst.total_amount) + ' ₺</small>';
                html += '</div></label>';

                index++;
            });

            html += '</div>';
        });

        html += '</div>';
        listContainer.innerHTML = html;

        // Event listeners
        document.querySelectorAll('.mews-inst-radio').forEach(function (radio) {
            radio. addEventListener('change', function () {
                var count = this.value;
                var bankId = this.getAttribute('data-bank-id');
                var total = parseFloat(this.getAttribute('data-total'));

                console.log('Mews POS: Installment selected:', {count, bankId, total});

                // Hidden inputları güncelle
                setInputValue('mews_installment_count', count);
                setInputValue('mews_bank_id', bankId);
                setInputValue('mews_total_amount', total);

                // Payment form amount'u güncelle
                var form = document.querySelector('form[data-mode="payment"]');
                if (form) {
                    form. setAttribute('data-amount', total. toFixed(2));
                }

                // Toplam tutarı güncelle
                document.querySelectorAll('.o_payment_amount').forEach(function (el) {
                    el.textContent = formatPrice(total) + ' ₺';
                });
            });
        });
    }

    // Helper functions
    function setInputValue(id, value) {
        var input = document.getElementById(id);
        if (input) {
            input.value = value;
        } else {
            // Input yoksa oluştur
            var form = document.querySelector('form[data-mode="payment"]');
            if (form) {
                var newInput = document.createElement('input');
                newInput.type = 'hidden';
                newInput.id = id;
                newInput. name = id;
                newInput.value = value;
                form.appendChild(newInput);
            }
        }
    }

    function formatPrice(price) {
        return parseFloat(price).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    }

    function escapeHtml(text) {
        var div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function debounce(func, wait) {
        var timeout;
        return function () {
            var context = this;
            var args = arguments;
            clearTimeout(timeout);
            timeout = setTimeout(function () {
                func.apply(context, args);
            }, wait);
        };
    }

    console.log('Mews POS: Ready');
})();
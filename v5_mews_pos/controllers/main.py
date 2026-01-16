# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
import logging
import re

_logger = logging.getLogger(__name__)


class MewsPosController(http.Controller):
    
    @http.route('/mews_pos/detect_bank', type='json', auth='public', website=True)
    def detect_bank(self, card_number='', **kwargs):
        """Kart numarasından banka tespiti"""
        
        try:
            # Sadece rakamları al
            card_clean = re.sub(r'\D', '', card_number)
            
            if len(card_clean) < 6:
                return {'success': False, 'error': 'Minimum 6 hane gerekli'}
            
            bin_number = card_clean[:6]
            _logger.info(f"BIN detection for:  {bin_number}")
            
            bank = request.env['mews.pos. bank'].sudo().get_bank_by_bin(bin_number)
            
            if bank:
                return {
                    'success': True,
                    'bank':  {
                        'id': bank. id,
                        'name':  bank.name,
                        'code': bank.code,
                        'logo': f'/web/image/mews. pos.bank/{bank.id}/logo' if bank.logo else False
                    }
                }
            else:
                return {
                    'success': False,
                    'error': 'Banka bulunamadı'
                }
                
        except Exception as e: 
            _logger.error(f"BIN detection error: {str(e)}", exc_info=True)
            return {'success': False, 'error': str(e)}
    
    @http.route('/mews_pos/get_payment_installments', type='json', auth='public', website=True)
    def get_payment_installments(self, amount=0. 0, bin_number='', **kwargs):
        """Ödeme sayfası için taksit seçenekleri"""
        
        _logger.info(f"Get installments:  amount={amount}, bin={bin_number}")
        
        try:
            amount = float(amount)
            
            if amount <= 0:
                return {'success': False, 'error': 'Geçersiz tutar'}
            
            provider = request.env['payment.provider'].sudo().search([
                ('code', '=', 'mews_pos'),
                ('state', '=', 'enabled')
            ], limit=1)
            
            if not provider:
                return {'success': False, 'error': 'Mews POS aktif değil'}
            
            if amount < provider.mews_min_installment_amount:
                return {
                    'success': True,
                    'installments':  [],
                    'message': f'Minimum tutar:  {provider.mews_min_installment_amount} TL'
                }
            
            # BIN'e göre filtreleme
            banks_to_use = []
            if bin_number:
                bank = request.env['mews. pos.bank'].sudo().get_bank_by_bin(bin_number)
                if bank: 
                    banks_to_use = [bank]
            
            if not banks_to_use:
                banks_to_use = provider.mews_bank_ids if provider.mews_bank_ids else \
                              request.env['mews.pos.bank'].sudo().search([('active', '=', True)])
            
            result = []
            for bank in banks_to_use:
                configs = bank.installment_config_ids. filtered(
                    lambda c: c.active and c.min_amount <= amount
                )
                
                if configs:
                    installments = []
                    for config in configs. sorted(key=lambda c: c.installment_count):
                        if config.installment_count <= provider.mews_max_installment:
                            inst_data = config.calculate_installment(amount)
                            installments. append(inst_data)
                    
                    if installments:
                        result.append({
                            'bank': {
                                'id': bank. id,
                                'name':  bank.name,
                                'code': bank.code,
                                'logo': f'/web/image/mews.pos.bank/{bank.id}/logo' if bank.logo else False
                            },
                            'installments':  installments
                        })
            
            _logger.info(f"Returning {len(result)} banks with installments")
            
            return {
                'success':  True,
                'installments':  result,
                'amount': amount
            }
            
        except Exception as e:
            _logger. error(f"Get installments error: {str(e)}", exc_info=True)
            return {'success': False, 'error': str(e)}
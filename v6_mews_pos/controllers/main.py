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
            card_clean = re.sub(r'\D', '', str(card_number))
            
            if len(card_clean) < 6:
                return {
                    'success': False, 
                    'error': 'Minimum 6 hane gerekli'
                }
            
            bin_number = card_clean[:6]
            _logger.info(f"Mews POS:  BIN detection for {bin_number}")
            
            # BIN'e göre banka bul
            bank = request.env['mews.pos. bank'].sudo().get_bank_by_bin(bin_number)
            
            if bank:
                return {
                    'success': True,
                    'bank':  {
                        'id': bank.id,
                        'name': bank.name,
                        'code': bank.code,
                        'logo': f'/web/image/mews. pos. bank/{bank.id}/logo' if bank.logo else None
                    }
                }
            
            return {
                'success':  False,
                'error': 'Banka bulunamadı'
            }
                
        except Exception as e: 
            _logger.error(f"Mews POS: BIN detection error - {str(e)}", exc_info=True)
            return {
                'success': False, 
                'error': f'Hata: {str(e)}'
            }
    
    @http.route('/mews_pos/get_payment_installments', type='json', auth='public', website=True)
    def get_payment_installments(self, amount=0.0, bin_number='', **kwargs):
        """Ödeme sayfası için taksit seçeneklerini getir"""
        
        _logger.info(f"Mews POS: Get installments - amount={amount}, bin={bin_number}")
        
        try:
            # Amount'u float'a çevir
            try:
                amount = float(amount)
            except (TypeError, ValueError):
                return {
                    'success': False, 
                    'error': 'Geçersiz tutar'
                }
            
            if amount <= 0:
                return {
                    'success': False, 
                    'error': 'Tutar sıfırdan büyük olmalı'
                }
            
            # Mews POS provider'ı bul
            provider = request.env['payment.provider'].sudo().search([
                ('code', '=', 'mews_pos'),
                ('state', '=', 'enabled')
            ], limit=1)
            
            if not provider:
                return {
                    'success': False, 
                    'error': 'Mews POS aktif değil'
                }
            
            _logger.info(f"Mews POS: Provider found - {provider.name}")
            
            # Minimum tutar kontrolü
            if amount < provider. mews_min_installment_amount:
                return {
                    'success': True,
                    'installments':  [],
                    'message': f'Minimum taksit tutarı:  {provider.mews_min_installment_amount} TL'
                }
            
            # BIN'e göre banka filtrele
            banks_to_use = []
            
            if bin_number:
                bank = request.env['mews. pos.bank'].sudo().get_bank_by_bin(bin_number)
                if bank: 
                    _logger.info(f"Mews POS: Bank detected from BIN - {bank.name}")
                    banks_to_use = [bank]
            
            # BIN'den banka bulunamadıysa tüm bankaları kullan
            if not banks_to_use: 
                if provider.mews_bank_ids:
                    banks_to_use = provider.mews_bank_ids
                else:
                    banks_to_use = request. env['mews.pos.bank'].sudo().search([
                        ('active', '=', True)
                    ])
            
            _logger.info(f"Mews POS: Using {len(banks_to_use)} bank(s)")
            
            # Taksit seçeneklerini oluştur
            result = []
            
            for bank in banks_to_use: 
                configs = bank.installment_config_ids.filtered(
                    lambda c: c.active and c. min_amount <= amount
                )
                
                if not configs:
                    continue
                
                installments = []
                for config in configs. sorted(key=lambda c: c.installment_count):
                    # Maksimum taksit kontrolü
                    if config.installment_count > provider.mews_max_installment:
                        continue
                    
                    # Taksit hesapla
                    inst_data = config.calculate_installment(amount)
                    installments.append(inst_data)
                
                if installments:
                    result.append({
                        'bank': {
                            'id':  bank.id,
                            'name': bank.name,
                            'code': bank.code,
                            'logo': f'/web/image/mews.pos.bank/{bank.id}/logo' if bank.logo else None
                        },
                        'installments': installments
                    })
            
            _logger.info(f"Mews POS:  Returning {len(result)} bank(s) with installments")
            
            return {
                'success': True,
                'installments': result,
                'amount': amount
            }
            
        except Exception as e:
            _logger. error(f"Mews POS: Get installments error - {str(e)}", exc_info=True)
            return {
                'success': False, 
                'error': f'Hata: {str(e)}'
            }
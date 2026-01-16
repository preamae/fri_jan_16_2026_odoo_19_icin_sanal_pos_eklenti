# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class MewsPosController(http.Controller):
    
    @http.route('/mews_pos/get_payment_installments', type='json', auth='public', website=True)
    def get_payment_installments(self, amount=0.0, **kwargs):
        """Ödeme sayfası için taksit seçeneklerini getir"""
        
        _logger.info(f"===== MEWS POS:  get_payment_installments called =====")
        _logger.info(f"Amount: {amount}")
        _logger.info(f"Kwargs: {kwargs}")
        
        try:
            amount = float(amount)
            
            if amount <= 0:
                return {'success': False, 'error': 'Invalid amount:  ' + str(amount)}
            
            # Mews POS provider'ı bul
            provider = request.env['payment.provider'].sudo().search([
                ('code', '=', 'mews_pos'),
                ('state', '=', 'enabled')
            ], limit=1)
            
            _logger.info(f"Provider found: {provider. name if provider else 'None'}")
            
            if not provider: 
                return {
                    'success': False, 
                    'error': 'Mews POS provider not found or not enabled'
                }
            
            # Minimum tutar kontrolü
            if amount < provider. mews_min_installment_amount:
                _logger.info(f"Amount {amount} < min {provider.mews_min_installment_amount}")
                return {
                    'success': True,
                    'installments':  [],
                    'message': f'Minimum taksit tutarı: {provider.mews_min_installment_amount} TL'
                }
            
            # Taksit seçeneklerini al
            installments_data = provider.get_available_installments(amount, [])
            
            _logger. info(f"Installments found: {len(installments_data)}")
            _logger.info(f"Installments data: {installments_data}")
            
            return {
                'success': True,
                'installments': installments_data,
                'amount': amount
            }
            
        except Exception as e:
            _logger.error(f"===== MEWS POS ERROR =====")
            _logger.error(f"Error: {str(e)}", exc_info=True)
            return {
                'success': False, 
                'error': str(e)
            }
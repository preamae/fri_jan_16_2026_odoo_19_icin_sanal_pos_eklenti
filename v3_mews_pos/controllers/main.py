# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class MewsPosController(http.Controller):
    
    @http.route('/mews_pos/get_payment_installments', type='json', auth='public', website=True)
    def get_payment_installments(self, amount=0.0, **kwargs):
        """Ödeme sayfası için taksit seçeneklerini getir"""
        
        try:
            amount = float(amount)
            
            if amount <= 0:
                return {'success': False, 'error': 'Invalid amount'}
            
            # Aktif Mews POS provider'ı bul
            provider = request.env['payment.provider'].sudo().search([
                ('code', '=', 'mews_pos'),
                ('state', '=', 'enabled')
            ], limit=1)
            
            if not provider:
                return {'success': False, 'error': 'Mews POS provider not found'}
            
            # Minimum tutar kontrolü
            if amount < provider. mews_min_installment_amount:
                return {
                    'success': True,
                    'installments':  [],
                    'message': f'Taksit için minimum tutar {provider.mews_min_installment_amount} TL'
                }
            
            # Sepetteki kategorileri al
            order = request.website.sale_get_order()
            category_ids = []
            if order:
                category_ids = order.order_line.mapped('product_id.public_categ_ids').ids
            
            # Taksit seçeneklerini al
            installments_data = provider.get_available_installments(amount, category_ids)
            
            return {
                'success': True,
                'installments': installments_data,
                'amount':  amount,
                'min_amount': provider.mews_min_installment_amount
            }
            
        except Exception as e:
            _logger.error(f"Error getting payment installments: {str(e)}", exc_info=True)
            return {'success': False, 'error': str(e)}
    
    @http.route('/mews_pos/process_payment', type='json', auth='public', website=True, csrf=False)
    def process_payment(self, **post):
        """Taksitli ödemeyi işle"""
        
        try:
            order = request.website.sale_get_order()
            
            if not order:
                return {'success': False, 'error': 'Order not found'}
            
            installment_count = int(post. get('installment_count', 1))
            bank_id = int(post.get('installment_bank_id', 0))
            installment_amount = float(post. get('installment_amount', 0))
            
            # Sipariş notuna ekle
            order.note = (order.note or '') + f"\nTaksit: {installment_count} x {installment_amount} TL"
            
            # Transaction oluştur
            tx_values = {
                'sale_order_ids': [(6, 0, [order.id])],
                'installment_count': installment_count,
                'bank_id': bank_id if bank_id > 0 else False,
            }
            
            return {'success': True, 'transaction':  tx_values}
            
        except Exception as e:
            _logger.error(f"Error processing payment: {str(e)}", exc_info=True)
            return {'success': False, 'error': str(e)}
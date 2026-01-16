# -*- coding:  utf-8 -*-

from odoo import http
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)


class MewsPosController(http.Controller):

    @http.route('/mews_pos/get_installments', type='json', auth='public', website=True)
    def get_installments(self, amount, category_ids=None, **kwargs):
        """AJAX ile taksit seçeneklerini getir"""
        provider = request.env['payment.provider'].sudo().search([
            ('code', '=', 'mews_pos'),
            ('state', '=', 'enabled')
        ], limit=1)
        
        if not provider: 
            return {'error': 'Mews POS sağlayıcısı bulunamadı'}
        
        try:
            amount = float(amount)
            if category_ids and isinstance(category_ids, str):
                category_ids = [int(c) for c in category_ids.split(',')]
            
            installments = provider._get_available_installments(amount, category_ids)
            return {'success': True, 'data': installments}
        except Exception as e:
            _logger.error(f"Taksit hesaplama hatası: {str(e)}")
            return {'error': str(e)}

    @http.route('/mews_pos/calculate', type='json', auth='public', website=True)
    def calculate_installment(self, bank_id, installment_count, amount, **kwargs):
        """Belirli taksit için hesaplama yap"""
        try:
            bank = request.env['mews.pos.bank'].sudo().browse(int(bank_id))
            if not bank.exists():
                return {'error': 'Banka bulunamadı'}
            
            config = bank.installment_config_ids.filtered(
                lambda c:  c.installment_count == int(installment_count) and c.active
            )
            
            if not config: 
                return {'error': 'Taksit yapılandırması bulunamadı'}
            
            result = config[0]. calculate_installment(float(amount))
            return {'success': True, 'data': result}
        except Exception as e:
            _logger.error(f"Taksit hesaplama hatası: {str(e)}")
            return {'error':  str(e)}

    @http.route('/mews_pos/callback/<string:status>/<string:transaction_id>', 
                type='http', auth='public', website=True, csrf=False, methods=['POST', 'GET'])
    def payment_callback(self, status, transaction_id, **kwargs):
        """Banka callback işlemi"""
        transaction = request.env['mews.pos. transaction'].sudo().search([
            ('transaction_id', '=', transaction_id)
        ], limit=1)
        
        if not transaction:
            return request.redirect('/shop/payment/error')
        
        if status == 'success': 
            transaction.write({
                'state': 'success',
                'bank_response_code': kwargs.get('mdStatus', ''),
                'bank_response_message':  kwargs.get('mdErrorMsg', ''),
                'auth_code': kwargs. get('AuthCode', ''),
                'response_data': json.dumps(kwargs),
            })
            return request.redirect('/shop/confirmation')
        else:
            transaction.write({
                'state': 'failed',
                'error_message': kwargs. get('ErrMsg', 'Ödeme başarısız'),
                'response_data': json. dumps(kwargs),
            })
            return request.redirect('/shop/payment/error')

    @http.route('/mews_pos/process', type='http', auth='public', 
                website=True, csrf=False, methods=['POST'])
    def process_payment(self, **kwargs):
        """3D Secure formunu oluştur ve banka sayfasına yönlendir"""
        order_id = kwargs.get('order_id')
        bank_id = kwargs. get('bank_id')
        installment = kwargs.get('installment', 1)
        
        # Kredi kartı bilgileri
        card_data = {
            'number': kwargs.get('card_number', '').replace(' ', ''),
            'month': kwargs.get('card_month'),
            'year':  kwargs.get('card_year'),
            'cvv': kwargs.get('card_cvv'),
            'name': kwargs.get('card_name'),
        }
        
        order = request.env['sale.order'].sudo().browse(int(order_id))
        bank = request.env['mews.pos. bank'].sudo().browse(int(bank_id))
        
        if not order or not bank:
            return request.redirect('/shop/payment/error')
        
        # İşlem kaydı oluştur
        installment_count = int(installment)
        config = bank.installment_config_ids. filtered(
            lambda c: c.installment_count == installment_count
        )
        
        if config:
            result = config[0].calculate_installment(order.amount_total)
            total_amount = result['total_amount']
            installment_amount = result['installment_amount']
        else:
            total_amount = order. amount_total
            installment_amount = order.amount_total
        
        transaction = request.env['mews.pos. transaction'].sudo().create({
            'order_id': order. id,
            'bank_id': bank. id,
            'amount': order.amount_total,
            'installment_count': installment_count,
            'installment_amount': installment_amount,
            'total_amount': total_amount,
            'card_number_masked': f"****-****-****-{card_data['number'][-4:]}",
            'card_holder_name': card_data['name'],
            'ip_address': request. httprequest.remote_addr,
            'state': 'pending',
        })
        
        # PHP servisine gönder ve 3D form'u al
        form_data = transaction._send_to_php_gateway()
        form_data['card'] = card_data
        
        # 3D Secure formu oluştur
        return request.render('mews_pos. threed_form', {
            'form_data': form_data,
            'bank':  bank,
            'transaction': transaction,
        })
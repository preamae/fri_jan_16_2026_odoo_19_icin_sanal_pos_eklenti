# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
import json


class MewsPosController(http.Controller):
    
    @http.route('/mews_pos/get_installments', type='json', auth='public', website=True)
    def get_product_installments(self, product_id=None, amount=None, **kwargs):
        """Ürün taksit seçeneklerini getir"""
        
        if not product_id:
            return {'error': 'Product ID required'}
        
        product = request.env['product.template'].sudo().browse(int(product_id))
        
        if not product.exists():
            return {'error': 'Product not found'}
        
        if amount: 
            amount = float(amount)
        else:
            amount = product.list_price
        
        installments = product._get_installment_display_data()
        
        return {
            'success': True,
            'product_id': product. id,
            'product_name': product.name,
            'amount': amount,
            'installments': installments,
        }
    
    @http.route('/mews_pos/cart_installments', type='json', auth='public', website=True)
    def get_cart_installments(self, **kwargs):
        """Sepet toplamı için taksit seçeneklerini getir"""
        
        order = request.website.sale_get_order()
        
        if not order:
            return {'error': 'No cart found'}
        
        amount = order.amount_total
        
        # Sepetteki kategorileri al
        category_ids = order.order_line.mapped('product_id.categ_id').ids
        
        result = []
        banks = request.env['mews. pos.bank'].sudo().search([('active', '=', True)], order='sequence')
        
        for bank in banks:
            configs = bank.installment_config_ids.filtered(
                lambda c: c.active and c. min_amount <= amount
            )
            
            if not configs: 
                continue
            
            installments = []
            for config in configs.sorted(key=lambda c: c.installment_count):
                inst_data = config.calculate_installment(amount)
                installments.append(inst_data)
            
            if installments: 
                result.append({
                    'bank_id': bank.id,
                    'bank_name': bank.name,
                    'bank_code': bank.code,
                    'installments': installments,
                })
        
        return {
            'success': True,
            'amount': amount,
            'installments': result,
        }
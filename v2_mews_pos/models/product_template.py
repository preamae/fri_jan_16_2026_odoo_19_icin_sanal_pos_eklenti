# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    installment_allowed = fields.Boolean(
        string='Taksit İzni',
        default=True,
        help='Bu ürün için taksitli satış yapılabilir mi?'
    )
    
    max_installment = fields.Integer(
        string='Maksimum Taksit',
        default=0,
        help='0 = Kategori ayarlarını kullan'
    )
    
    min_installment_amount = fields.Float(
        string='Minimum Taksit Tutarı',
        digits=(12, 2),
        default=0.0,
        help='Taksitli satış için minimum tutar'
    )

    def get_installment_options(self, bank_id=None):
        """Ürün için taksit seçeneklerini getir"""
        self.ensure_one()
        
        if not self.installment_allowed:
            return []
        
        if self.max_installment > 0:
            max_inst = self.max_installment
        else: 
            if bank_id:
                max_inst = self.categ_id.get_max_installment_for_bank(bank_id)
            else:
                max_inst = self.categ_id.max_installment_global
        
        return {
            'max_installment': max_inst,
            'min_amount': self.min_installment_amount,
            'category_id': self.categ_id.id,
        }
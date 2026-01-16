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

    def _get_installment_display_data(self):
        """Ürün sayfası için taksit verilerini hazırla"""
        self.ensure_one()
        
        if not self.installment_allowed:
            return []
        
        amount = self.list_price
        if amount < self.min_installment_amount:
            return []
        
        result = []
        banks = self.env['mews. pos.bank'].search([('active', '=', True)], order='sequence')
        
        for bank in banks:
            configs = bank.installment_config_ids. filtered(
                lambda c: c.active and c.min_amount <= amount
            )
            
            if not configs:
                continue
            
            # Kategori kısıtlamalarını kontrol et
            max_allowed = 36
            if self.categ_id:
                restriction = bank.category_restriction_ids.filtered(
                    lambda r: r.category_id. id == self.categ_id.id
                )
                if restriction: 
                    if not restriction[0].installment_allowed:
                        continue
                    max_allowed = restriction[0].max_installment
            
            # Ürün bazlı max kontrolü
            if self.max_installment > 0:
                max_allowed = min(max_allowed, self.max_installment)
            
            installments = []
            for config in configs. sorted(key=lambda c: c.installment_count):
                if config.installment_count > max_allowed:
                    continue
                
                inst_data = config.calculate_installment(amount)
                installments.append(inst_data)
            
            if installments:
                result.append({
                    'bank_id': bank.id,
                    'bank_name': bank.name,
                    'bank_code': bank.code,
                    'logo': bank.logo,
                    'color': self._get_bank_color(bank. code),
                    'installments': installments,
                })
        
        return result
    
    def _get_bank_color(self, bank_code):
        """Banka renk kodları"""
        colors = {
            'akbank': '#f15a29',
            'garanti': '#00a650',
            'yapikredi': '#005eb8',
            'isbank': '#004b93',
            'qnb': '#006341',
            'denizbank': '#00a551',
            'halkbank': '#e30613',
            'vakifbank': '#e2001a',
            'ziraat': '#ed1c24',
        }
        return colors.get(bank_code. lower(), '#6c757d')

    def get_installment_options(self, amount=None):
        """API için taksit seçeneklerini getir"""
        self.ensure_one()
        
        if not self.installment_allowed:
            return []
        
        if amount is None:
            amount = self.list_price
        
        return self._get_installment_display_data()
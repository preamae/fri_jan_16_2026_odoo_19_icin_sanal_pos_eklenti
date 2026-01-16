# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class PaymentProvider(models. Model):
    _inherit = 'payment. provider'

    code = fields.Selection(
        selection_add=[('mews_pos', 'Mews POS')],
        ondelete={'mews_pos': 'set default'}
    )
    
    mews_bank_ids = fields.Many2many(
        'mews.pos.bank',
        string='Aktif Bankalar',
        help='Bu ödeme sağlayıcısı için aktif bankalar'
    )
    
    mews_show_installments = fields.Boolean(
        string='Taksit Seçeneklerini Göster',
        default=True
    )
    
    mews_default_installment = fields.Integer(
        string='Varsayılan Taksit',
        default=1,
        help='Varsayılan taksit sayısı (1 = Tek çekim)'
    )

    def _get_available_installments(self, amount, category_ids=None):
        """Mevcut taksit seçeneklerini getir"""
        self.ensure_one()
        
        if self.code != 'mews_pos':
            return []
        
        result = []
        
        for bank in self.mews_bank_ids. filtered(lambda b:  b.active):
            bank_installments = []
            
            # Taksit yapılandırmalarını al
            configs = bank.installment_config_ids.filtered(
                lambda c: c. active and c.min_amount <= amount
            )
            
            for config in configs:
                inst_data = config.calculate_installment(amount)
                inst_data['bank_id'] = bank. id
                inst_data['bank_name'] = bank.name
                inst_data['bank_code'] = bank.code
                inst_data['bank_logo'] = bank.logo
                
                # Kategori kısıtlamalarını uygula
                if category_ids: 
                    restrictions = bank.category_restriction_ids.filtered(
                        lambda r:  r.category_id. id in category_ids
                    )
                    
                    if restrictions: 
                        # En kısıtlayıcı olanı al
                        max_allowed = min(r.max_installment for r in restrictions)
                        if inst_data['installment_count'] > max_allowed:
                            continue
                        
                        # Engellenen taksitleri kontrol et
                        blocked = []
                        for r in restrictions:
                            blocked.extend(r. get_blocked_installment_list())
                        if inst_data['installment_count'] in blocked:
                            continue
                        
                        # Taksit izni kontrolü
                        if not all(r.installment_allowed for r in restrictions):
                            continue
                
                bank_installments.append(inst_data)
            
            if bank_installments: 
                result.append({
                    'bank':  {
                        'id': bank.id,
                        'name': bank.name,
                        'code': bank.code,
                        'logo': bank.logo,
                    },
                    'installments': sorted(
                        bank_installments, 
                        key=lambda x: x['installment_count']
                    )
                })
        
        return result
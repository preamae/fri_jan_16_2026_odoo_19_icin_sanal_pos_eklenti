# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[('mews_pos', 'Mews POS')],
        ondelete={'mews_pos':  'cascade'}
    )

    mews_bank_ids = fields.Many2many(
        'mews.pos.bank',
        'payment_provider_mews_bank_rel',
        'provider_id',
        'bank_id',
        string='Mews POS Bankaları'
    )
    
    mews_show_installments = fields.Boolean(
        string='Taksit Göster',
        default=True
    )
    
    mews_max_installment = fields.Integer(
        string='Maksimum Taksit',
        default=12
    )
    
    mews_min_installment_amount = fields.Float(
        string='Minimum Taksit Tutarı',
        default=100. 0
    )


class MewsPosBank(models.Model):
    _inherit = 'mews.pos. bank'
    
    bin_ranges = fields.Text(
        string='BIN Aralıkları',
        help='Virgülle ayrılmış BIN numaraları (örn: 540668,557835,454360)'
    )
    
    def get_bank_by_bin(self, bin_number):
        """BIN numarasına göre banka bul"""
        if not bin_number or len(str(bin_number)) < 6:
            return False
        
        bin_str = str(bin_number)[: 6]
        
        banks = self.search([('active', '=', True)])
        for bank in banks:
            if bank.bin_ranges:
                bin_list = [b.strip() for b in bank.bin_ranges.split(',')]
                if bin_str in bin_list: 
                    return bank
        
        return False
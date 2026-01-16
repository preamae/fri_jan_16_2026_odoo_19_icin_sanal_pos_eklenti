# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class MewsPosBank(models.  Model):
    """Sanal POS Banka Tanımları"""
    _name = 'mews.pos.bank'
    _description = 'Mews POS Banka'
    _order = 'sequence, name'

    name = fields. Char(string='Banka Adı', required=True)
    code = fields.Char(string='Banka Kodu', required=True)
    sequence = fields.Integer(string='Sıra', default=10)
    active = fields.Boolean(string='Aktif', default=True)
    
    # BIN Aralıkları
    bin_ranges = fields.Text(
        string='BIN Aralıkları',
        help='Virgülle ayrılmış 6 haneli BIN numaraları (örn: 540668,557835,454360)'
    )
    
    # Gateway Ayarları
    gateway_type = fields.  Selection([
        ('akbank_pos', 'Akbank POS'),
        ('garanti_pos', 'Garanti BBVA POS'),
        ('posnet', 'YapıKredi Posnet'),
        ('estv3_pos', 'İşbank EST V3'),
        ('nestpay', 'Nestpay (Generic)'),
        ('custom', 'Özel Entegrasyon'),
    ], string='Gateway Tipi', default='nestpay')
    
    payment_model = fields.Selection([
        ('3d_secure', '3D Secure'),
        ('3d_pay', '3D Pay'),
        ('non_3d', 'Non-3D'),
    ], string='Ödeme Modeli', default='3d_secure', required=True)
    
    environment = fields.Selection([
        ('test', 'Test'),
        ('production', 'Production'),
    ], string='Ortam', default='test', required=True)
    
    # API Ayarları
    merchant_id = fields.Char(string='Merchant ID')
    terminal_id = fields.Char(string='Terminal ID')
    store_key = fields.Char(string='Store Key')
    client_id = fields.Char(string='Client ID')
    username = fields.Char(string='API Username')
    password = fields. Char(string='API Password')
    
    # URL'ler
    payment_api_url = fields.Char(string='Payment API URL')
    gateway_3d_url = fields.Char(string='3D Gateway URL')
    
    # Logo
    logo = fields.Binary(string='Logo')
    
    # İlişkiler
    installment_config_ids = fields.One2many(
        'mews. pos.installment. config',
        'bank_id',
        string='Taksit Yapılandırmaları'
    )
    
    category_restriction_ids = fields.One2many(
        'mews.pos.  category.restriction',
        'bank_id',
        string='Kategori Kısıtlamaları'
    )

    @api.model
    def get_bank_by_bin(self, bin_number):
        """BIN numarasına göre banka bul"""
        if not bin_number:
            return self.env['mews.pos. bank']
        
        # BIN'i string'e çevir ve ilk 6 haneyi al
        bin_str = str(bin_number).replace(' ', '').replace('-', '')[:6]
        
        if len(bin_str) < 6:
            return self.env['mews.pos. bank']
        
        # Tüm aktif bankaları kontrol et
        banks = self.search([('active', '=', True)])
        
        for bank in banks:
            if bank.bin_ranges:
                # Virgülle ayrılmış BIN listesi
                bin_list = [b.strip() for b in bank.bin_ranges.split(',') if b.strip()]
                
                if bin_str in bin_list: 
                    return bank
        
        return self.env['mews.pos.bank']
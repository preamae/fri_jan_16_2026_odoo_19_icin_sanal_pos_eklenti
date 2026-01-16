# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo. exceptions import ValidationError


class MewsPosBank(models.Model):
    """Banka tanımlamaları ve POS yapılandırması"""
    _name = 'mews.pos.bank'
    _description = 'Mews POS Banka Tanımı'
    _order = 'sequence, name'

    name = fields.Char(string='Banka Adı', required=True)
    code = fields.Char(string='Banka Kodu', required=True)
    sequence = fields.Integer(string='Sıra', default=10)
    active = fields.Boolean(string='Aktif', default=True)
    
    # Gateway Tipi
    gateway_type = fields.Selection([
        ('akbank_pos', 'Akbank POS'),
        ('estv3_pos', 'EST V3 POS (Payten/Asseco)'),
        ('garanti_pos', 'Garanti POS'),
        ('posnet', 'PosNet (YapıKredi)'),
        ('posnet_v1', 'PosNet V1 (Albaraka)'),
        ('payfor', 'PayFor (Finansbank)'),
        ('payflex_mpi', 'PayFlex MPI (Ziraat/Vakıfbank)'),
        ('payflex_common', 'PayFlex Common Payment'),
        ('interpos', 'InterPos (Denizbank)'),
        ('kuveyt_pos', 'Kuveyt POS'),
        ('vakif_katilim', 'Vakıf Katılım POS'),
        ('tosla', 'Tosla'),
        ('param_pos', 'ParamPos'),
    ], string='Gateway Tipi', required=True)
    
    # Ödeme Modeli
    payment_model = fields.Selection([
        ('3d_secure', '3D Secure'),
        ('3d_pay', '3D Pay'),
        ('3d_host', '3D Host'),
        ('non_secure', 'Non Secure'),
    ], string='Ödeme Modeli', default='3d_secure', required=True)
    
    # API Bilgileri
    merchant_id = fields. Char(string='Üye İşyeri No')
    terminal_id = fields.Char(string='Terminal No')
    username = fields.Char(string='Kullanıcı Adı')
    password = fields.Char(string='Şifre')
    store_key = fields.Char(string='Store Key / 3D Secure Key')
    client_id = fields.Char(string='Client ID')
    
    # Endpoint'ler
    payment_api_url = fields.Char(string='Payment API URL')
    gateway_3d_url = fields.Char(string='3D Gateway URL')
    gateway_3d_host_url = fields.Char(string='3D Host Gateway URL')
    
    # Test/Canlı Mod
    environment = fields.Selection([
        ('test', 'Test Ortamı'),
        ('production', 'Canlı Ortam'),
    ], string='Ortam', default='test', required=True)
    
    # Görsel
    logo = fields.Binary(string='Banka Logosu')
    
    # Taksit Yapılandırması
    installment_config_ids = fields.One2many(
        'mews.pos.installment. config',
        'bank_id',
        string='Taksit Yapılandırmaları'
    )
    
    # Kategori Kısıtlamaları
    category_restriction_ids = fields. One2many(
        'mews.pos.category.restriction',
        'bank_id',
        string='Kategori Kısıtlamaları'
    )

    _sql_constraints = [
        ('code_unique', 'unique(code)', 'Banka kodu benzersiz olmalıdır!')
    ]

    def get_gateway_class(self):
        """PHP Gateway sınıfını döndür"""
        gateway_mapping = {
            'akbank_pos': 'Mews\\Pos\\Gateways\\AkbankPos',
            'estv3_pos': 'Mews\\Pos\\Gateways\\EstV3Pos',
            'garanti_pos': 'Mews\\Pos\\Gateways\\GarantiPos',
            'posnet': 'Mews\\Pos\\Gateways\\PosNet',
            'posnet_v1': 'Mews\\Pos\\Gateways\\PosNetV1',
            'payfor': 'Mews\\Pos\\Gateways\\PayForPos',
            'payflex_mpi': 'Mews\\Pos\\Gateways\\PayFlexV4Pos',
            'payflex_common': 'Mews\\Pos\\Gateways\\PayFlexCPV4Pos',
            'interpos': 'Mews\\Pos\\Gateways\\InterPos',
            'kuveyt_pos': 'Mews\\Pos\\Gateways\\KuveytPos',
            'vakif_katilim':  'Mews\\Pos\\Gateways\\VakifKatilimPos',
            'tosla': 'Mews\\Pos\\Gateways\\ToslaPos',
            'param_pos': 'Mews\\Pos\\Gateways\\ParamPos',
        }
        return gateway_mapping.get(self.gateway_type)

    def get_account_config(self):
        """Python için hesap yapılandırmasını döndür"""
        return {
            'bank_code': self.code,
            'merchant_id': self.merchant_id,
            'terminal_id':  self.terminal_id,
            'username': self.username,
            'password': self.password,
            'store_key': self.store_key,
            'client_id': self.client_id,
            'gateway_class': self.get_gateway_class(),
            'payment_model': self.payment_model,
            'environment': self. environment,
            'endpoints': {
                'payment_api': self.payment_api_url,
                'gateway_3d': self.gateway_3d_url,
                'gateway_3d_host': self.gateway_3d_host_url,
            }
        }
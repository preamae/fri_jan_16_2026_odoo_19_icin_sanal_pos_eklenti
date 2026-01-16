# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json
import uuid
import logging

_logger = logging.getLogger(__name__)


class MewsPosTransaction(models.Model):
    """POS işlem kayıtları"""
    _name = 'mews.pos. transaction'
    _description = 'Mews POS İşlem Kaydı'
    _order = 'create_date desc'
    _rec_name = 'transaction_id'

    transaction_id = fields.Char(
        string='İşlem ID',
        required=True,
        readonly=True,
        default=lambda self: str(uuid. uuid4())
    )
    
    order_id = fields.Many2one(
        'sale.order',
        string='Sipariş',
        ondelete='set null'
    )
    
    bank_id = fields.Many2one(
        'mews.pos.bank',
        string='Banka',
        required=True,
        ondelete='restrict'
    )
    
    amount = fields.Float(string='Tutar', digits=(12, 2), required=True)
    currency = fields.Selection([
        ('TRY', 'Türk Lirası'),
        ('USD', 'Amerikan Doları'),
        ('EUR', 'Euro'),
        ('GBP', 'İngiliz Sterlini'),
    ], string='Para Birimi', default='TRY', required=True)
    
    installment_count = fields.Integer(string='Taksit Sayısı', default=1)
    installment_amount = fields.Float(string='Taksit Tutarı', digits=(12, 2))
    total_amount = fields.Float(string='Toplam Tutar', digits=(12, 2))
    interest_amount = fields.Float(
        string='Faiz Tutarı',
        digits=(12, 2),
        compute='_compute_interest_amount',
        store=True
    )
    
    card_number_masked = fields.Char(string='Kart No (Maskeli)')
    card_holder_name = fields.Char(string='Kart Sahibi')
    card_type = fields.Selection([
        ('visa', 'Visa'),
        ('mastercard', 'Mastercard'),
        ('amex', 'American Express'),
        ('troy', 'Troy'),
    ], string='Kart Tipi')
    card_bank_name = fields.Char(string='Kart Bankası')
    
    state = fields.Selection([
        ('draft', 'Taslak'),
        ('pending', 'Beklemede'),
        ('processing', 'İşleniyor'),
        ('waiting_3d', '3D Bekleniyor'),
        ('success', 'Başarılı'),
        ('failed', 'Başarısız'),
        ('cancelled', 'İptal Edildi'),
        ('refunded', 'İade Edildi'),
        ('partial_refund', 'Kısmi İade'),
    ], string='Durum', default='draft', required=True, tracking=True)
    
    bank_response_code = fields.Char(string='Banka Yanıt Kodu')
    bank_response_message = fields.Text(string='Banka Yanıt Mesajı')
    bank_order_id = fields.Char(string='Banka Sipariş No')
    auth_code = fields.Char(string='Onay Kodu')
    rrn = fields.Char(string='RRN')
    host_ref_num = fields.Char(string='Host Referans No')
    
    is_3d_secure = fields. Boolean(string='3D Secure', default=False)
    threed_status = fields. Char(string='3D Durum')
    md_status = fields.Char(string='MD Status')
    eci = fields.Char(string='ECI')
    cavv = fields.Char(string='CAVV')
    xid = fields.Char(string='XID')
    
    ip_address = fields.Char(string='IP Adresi')
    user_agent = fields. Text(string='User Agent')
    request_data = fields.Text(string='İstek Verisi')
    response_data = fields.Text(string='Yanıt Verisi')
    error_message = fields.Text(string='Hata Mesajı')
    error_code = fields.Char(string='Hata Kodu')
    
    refunded_amount = fields.Float(string='İade Edilen Tutar', digits=(12, 2), default=0)
    refund_ids = fields.One2many(
        'mews.pos.refund',
        'transaction_id',
        string='İade İşlemleri'
    )
    
    processed_at = fields.Datetime(string='İşlem Tarihi')
    cancelled_at = fields.Datetime(string='İptal Tarihi')

    @api.depends('amount', 'total_amount')
    def _compute_interest_amount(self):
        for record in self:
            record.interest_amount = record.total_amount - record.amount

    def _get_callback_url(self, status):
        """Callback URL oluştur"""
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return f"{base_url}/mews_pos/callback/{status}/{self.transaction_id}"

    def _detect_card_type(self, card_number):
        """Kart tipini tespit et"""
        if not card_number:
            return None
        
        card_number = card_number.replace(' ', '').replace('-', '')
        
        if card_number.startswith('4'):
            return 'visa'
        elif card_number[: 2] in ['51', '52', '53', '54', '55']:
            return 'mastercard'
        elif card_number[:2] in ['34', '37']: 
            return 'amex'
        elif card_number. startswith('9792'):
            return 'troy'
        
        return None


class MewsPosRefund(models.Model):
    """İade kayıtları"""
    _name = 'mews.pos.refund'
    _description = 'Mews POS İade Kaydı'
    _order = 'create_date desc'

    transaction_id = fields.Many2one(
        'mews.pos.transaction',
        string='Orijinal İşlem',
        required=True,
        ondelete='cascade'
    )
    
    amount = fields.Float(string='İade Tutarı', digits=(12, 2), required=True)
    
    state = fields.Selection([
        ('pending', 'Beklemede'),
        ('success', 'Başarılı'),
        ('failed', 'Başarısız'),
    ], string='Durum', default='pending', required=True)
    
    refund_ref = fields.Char(string='İade Referans No')
    response_data = fields.Text(string='Yanıt Verisi')
    error_message = fields.Text(string='Hata Mesajı')
    
    processed_at = fields. Datetime(string='İşlem Tarihi')
    notes = fields.Text(string='Notlar')
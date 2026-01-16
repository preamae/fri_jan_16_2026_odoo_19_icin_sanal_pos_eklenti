# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json
import uuid

_logger = logging.getLogger(__name__)


class MewsPosTransaction(models.Model):
    """POS işlem kayıtları"""
    _name = 'mews. pos.transaction'
    _description = 'Mews POS İşlem Kaydı'
    _order = 'create_date desc'
    _rec_name = 'transaction_id'

    # ...  (önceki fieldlar aynı kalacak)

    def action_process_payment(self, card_data):
        """Ödeme işlemini başlat - Python Gateway ile"""
        self.ensure_one()
        
        from .. services.payment_gateway_service import PaymentGatewayService
        gateway = PaymentGatewayService(self.env)
        
        self.write({
            'state': 'processing',
            'card_type': self._detect_card_type(card_data. get('number', '')),
        })
        
        if self.bank_id.payment_model == 'non_secure':
            # Non-Secure ödeme
            result = gateway.process_non_secure_payment(self, card_data)
            self._handle_payment_result(result)
        else:
            # 3D Secure form oluştur
            self. write({'state': 'waiting_3d', 'is_3d_secure': True})
            form_result = gateway.create_3d_form(self, card_data)
            return form_result. get('data')
        
        return None
    
    def action_process_3d_callback(self, callback_data):
        """3D Secure callback işle - Python Gateway ile"""
        self. ensure_one()
        
        from ..services.payment_gateway_service import PaymentGatewayService
        gateway = PaymentGatewayService(self.env)
        
        self.write({'state': 'processing'})
        
        result = gateway.process_3d_callback(self, callback_data)
        self._handle_payment_result(result)
        
        return self. state == 'success'
    
    def action_cancel(self):
        """İşlemi iptal et - Python Gateway ile"""
        self. ensure_one()
        
        if self.state != 'success':
            raise UserError(_('Sadece başarılı işlemler iptal edilebilir! '))
        
        from ..services.payment_gateway_service import PaymentGatewayService
        gateway = PaymentGatewayService(self.env)
        
        result = gateway.process_cancel(self)
        
        if result.get('success'):
            self.write({
                'state': 'cancelled',
                'cancelled_at': fields.Datetime.now(),
                'response_data': json.dumps(result, indent=2, ensure_ascii=False),
            })
            return True
        else:
            raise UserError(_('İptal işlemi başarısız:  %s') % result.get('error', 'Bilinmeyen hata'))
    
    # ... (diğer metodlar aynı kalacak)
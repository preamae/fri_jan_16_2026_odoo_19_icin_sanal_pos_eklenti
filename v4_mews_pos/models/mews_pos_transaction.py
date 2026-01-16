# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json
import uuid
import logging

_logger = logging.getLogger(__name__)


class MewsPosTransaction(models.Model):
    """POS işlem kayıtları"""
    _name = 'mews.pos.transaction'  # Boşluk kaldırıldı
    _description = 'Mews POS İşlem Kaydı'
    _order = 'create_date desc'
    _rec_name = 'transaction_id'

    # ...  (alanlar aynı kalacak, sadece _name değişti)
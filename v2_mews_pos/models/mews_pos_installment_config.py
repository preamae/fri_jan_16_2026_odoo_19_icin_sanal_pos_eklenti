# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class MewsPosInstallmentConfig(models. Model):
    """Banka bazlı taksit yapılandırması"""
    _name = 'mews.pos.installment. config'  # DÜZELT
    _description = 'Mews POS Taksit Yapılandırması'
    _order = 'bank_id, installment_count'

    # ...  (devamı aynı)
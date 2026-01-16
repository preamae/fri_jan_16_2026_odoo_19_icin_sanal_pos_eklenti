# İlk satırları gösteriyorum, tam dosya çok uzun

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class MewsPosCategoryRestriction(models.Model):
    """Kategori bazlı taksit kısıtlamaları"""
    _name = 'mews.pos.category. restriction'  # Boşluklar kaldırıldı
    _description = 'Mews POS Kategori Taksit Kısıtlaması'
    _order = 'bank_id, category_id'
    
    # Constraint'leri de güncelleyelim
    _sql_constraints = [
        ('bank_category_unique', 
         'unique(bank_id, category_id)', 
         'Her banka-kategori kombinasyonu benzersiz olmalıdır!')
    ]
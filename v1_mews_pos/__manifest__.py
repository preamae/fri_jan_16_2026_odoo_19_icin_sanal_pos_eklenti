# -*- coding: utf-8 -*-
{
    'name':  'Mews Sanal POS Entegrasyonu',
    'version': '19.0.1.0.0',
    'category': 'Accounting/Payment',
    'summary': 'Türk bankaları için sanal POS entegrasyonu - Kategori bazlı taksit sınırlaması',
    'description': """
        Mews POS Kütüphanesi Entegrasyonu
        ==================================
        
        Özellikler:
        - Çoklu banka desteği (Akbank, Garanti, YapıKredi, İşbank, vb.)
        - Kategori bazlı taksit sınırlaması
        - Ürün bazlı taksit seçenekleri
        - Taksit tutarı ve toplam tutar hesaplama
        - 3D Secure / Non-Secure ödeme desteği
        
        Desteklenen Bankalar:
        - Akbank (AkbankPos, EstV3Pos)
        - Garanti BBVA
        - YapıKredi (PosNet)
        - İşbank (EstV3Pos)
        - QNB Finansbank (PayFor)
        - Ziraat Bankası (PayFlex)
        - Vakıfbank (PayFlex)
        - Denizbank (InterPos)
        - Kuveyt Türk
        - Ve diğerleri... 
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'license':  'LGPL-3',
    'depends': [
        'base',
        'sale',
        'payment',
        'product',
        'website_sale',
    ],
    'data': [
        'security/ir.model.access. csv',
        'data/payment_provider_data.xml',
        'views/payment_provider_views.xml',
        'views/product_category_views.xml',
        'views/product_template_views.xml',
        'views/installment_views.xml',
        'views/templates. xml',
        'wizards/installment_calculator_wizard_views.xml',
    ],
    'assets': {
        'web. assets_frontend': [
            'mews_pos/static/src/js/installment_calculator. js',
            'mews_pos/static/src/css/installment. css',
        ],
    },
    'external_dependencies': {
        'python': ['requests'],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
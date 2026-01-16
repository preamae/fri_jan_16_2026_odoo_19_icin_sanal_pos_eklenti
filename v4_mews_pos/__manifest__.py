# -*- coding: utf-8 -*-
{
    'name': 'Mews Sanal POS Entegrasyonu',
    'version': '19.0.1.0.0',
    'category': 'Accounting/Payment',
    'summary': 'Türk bankaları için sanal POS entegrasyonu - Kategori bazlı taksit sınırlaması',
    'description': """
        Mews POS Python Entegrasyonu
        ============================
        
        Özellikler:
        - Çoklu banka desteği (Akbank, Garanti, YapıKredi, İşbank, vb.)
        - Kategori bazlı taksit sınırlaması
        - Ürün bazlı taksit seçenekleri
        - Taksit tutarı ve toplam tutar hesaplama
        - 3D Secure / Non-Secure ödeme desteği
        - Saf Python implementasyonu (PHP gerektirmez)
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'sale',
        'payment',  # ÖNEMLİ: payment modülü eklendi
        'product',
        'website_sale',
    ],
    'data': [
        'security/ir. model.access.csv',
        'data/payment_provider_data.xml',
        'views/payment_provider_views.xml',
        'views/product_category_views.xml',
        'views/product_template_views.xml',
        'views/installment_views.xml',
        'views/templates.xml',
        'views/installment_calculator_wizard_views.xml',
        'views/refund_wizard_views.xml',
        'views/dashboard_views.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'mews_pos/static/src/js/installment_calculator.js',
            'mews_pos/static/src/css/installment. css',
        ],
    },
    'external_dependencies': {
        'python': [
            'requests',
            'zeep',
            'cryptography',
            'lxml',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
{
    'name': 'Mews Sanal POS Entegrasyonu',
    'version': '19.0.1.0.0',
    'category': 'Accounting/Payment',
    'depends': [
        'base',
        'sale',
        'payment',
        'product',
        'website_sale',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/payment_provider_views.xml',
        'views/product_public_category_views.xml',
        'views/product_template_views.xml',
        'views/installment_views.xml',
        'views/templates.xml',
        'data/payment_provider_data.xml',
    ],
    'assets': {
        'web.assets_frontend':  [
            'mews_pos/static/src/css/installment.css',
            'mews_pos/static/src/js/payment_installments.js',
        ],
    },
    'installable': True,
    'application': True,
}
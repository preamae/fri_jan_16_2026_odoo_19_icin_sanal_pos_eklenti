_name = 'mews.pos.transaction'
# Ve içindeki Many2one referansları: 
bank_id = fields.Many2one('mews.pos.bank', ...)
order_id = fields.Many2one('sale.order', ...)
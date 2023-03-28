# -*- coding: utf-8 -*-
from odoo import models, fields, api


class StockConfirm(models.Model):
    
    _inherit = 'stock.picking'
    
    
    receive_merch = fields.Boolean(default=False)
    
    @api.depends("receive_merch")
    def mostrar_validar(self):
        self.receive_merch = True
        
        message = '\u2003\u2003•\u2003Estado: Mercadería Recibida'
        self.message_post(body=message)

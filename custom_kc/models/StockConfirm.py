# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.http import request

class StockLocation(models.Model):
    
    _inherit = 'stock.location'

    user_assigning = fields.Many2many('res.users','user_id')
    

class StockPicking(models.Model):
    
    _inherit = 'stock.picking'
    
    
    receive_merch = fields.Boolean(default=False)
    sale_id = fields.Many2one('sale.order',"Pedido de Venta")
    visible =fields.Boolean('Visible', compute='_is_visible', store=True, default=False)
    user_id = request.env.user.id
    
    
    @api.depends("location_dest_id")
    def _is_visible(self):
        for record in self:
            if record.location_dest_id.user_assigning.id == record.user_id: 
                record.visible = True
            else:
                record.visible = False
    
    
    
    @api.depends("receive_merch")
    def mostrar_validar(self):
        self.receive_merch = True
        
        message = '\u2003\u2003•\u2003Estado: Mercadería Recibida'
        self.message_post(body=message)

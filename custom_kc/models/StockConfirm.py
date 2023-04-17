# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.http import request

class StockLocation(models.Model):
    
    _inherit = 'stock.location'

    user_assigning = fields.Many2many('res.users')
    

class StockLocation(models.Model):
    
    _inherit = 'stock.picking.type'

    receive_merch_internal = fields.Boolean("Recibir Mercadería", default=False)





class StockPicking(models.Model):
    
    _inherit = 'stock.picking'
    
    
    receive_merch = fields.Boolean(default=False)
    sale_id = fields.Many2one('sale.order',"Pedido de Venta")
    visible =fields.Boolean('Visible', compute='_is_visible', store=True, default=False)
    visible_picking =fields.Boolean(compute='_visible', store=True)

    @api.depends("picking_type_id")
    def _visible(self):  
        for record in self:
            if record.picking_type_id.receive_merch_internal: 
                record.visible_picking = True
            else:
                record.visible_picking = False
                self.receive_merch = True


                        
    @api.depends("location_dest_id")
    def _is_visible(self):
        user_id = self.env.user
        for record in self:
            if user_id.id in record.location_dest_id.user_assigning.ids: 
                record.visible = False
            else:
                record.visible = True

                
    @api.depends("receive_merch")
    def mostrar_validar(self):
        self.receive_merch = True
        
        message = '\u2003\u2003•\u2003Estado: Mercadería Recibida'
        self.message_post(body=message)

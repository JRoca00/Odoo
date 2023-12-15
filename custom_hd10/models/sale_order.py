# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.http import request

class ResConfigSettings(models.TransientModel):
    
    _inherit = 'res.config.settings'

    user_assigning = fields.Many2many('res.users')
    

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        user_assigning_ids = [(6, 0, self.user_assigning.ids)]
        self.env['ir.config_parameter'].set_param('custom_hd10.user_assigning_ids', user_assigning_ids)


    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        user_assigning_ids = self.env['ir.config_parameter'].get_param('custom_hd10.user_assigning_ids')
        if user_assigning_ids:
            user_assigning_ids = eval(user_assigning_ids)
        res['user_assigning'] = user_assigning_ids[0][2] if user_assigning_ids else []
        return res




class SaleOrder(models.Model):
    _inherit = 'sale.order'

    confirm_co = fields.Boolean(default=True)
    accepted_co = fields.Boolean(default=False, compute='compute_accepted_co')
    visible = fields.Boolean(default=True)
    visibleval = fields.Boolean(default=True)

    @api.onchange('amount_total')
    def compute_accepted_co(self):
        for order in self:
            if order.amount_total >= 10000:
                self.confirm_co = False
                user_assigning_ids = self.env['ir.config_parameter'].sudo().get_param('custom_hd10.user_assigning_ids')
                if user_assigning_ids:
                    user_assigning_ids = eval(user_assigning_ids)
                    user_ids = user_assigning_ids[0][2] if user_assigning_ids else []
                    if self.env.user.id in user_ids:
                        order.accepted_co = True
                    else:
                        order.accepted_co = False
                else:
                    order.accepted_co = False
            else:
                order.accepted_co = False
                self.confirm_co = True


    @api.depends("confirm_co")
    def action_accept_quotation(self):
        self.visible = False
        self.visibleval = False
        self.confirm_co = True
        message = 'Cotización Aceptada'
        self.message_post(body=message)







"""class StockPicking(models.Model):

    receive_merch = fields.Boolean(default=False)
                
    @api.depends("receive_merch")
    def mostrar_validar(self):
        self.receive_merch = True
        message = '\u2003\u2003•\u2003Estado: Mercadería Recibida'
        self.message_post(body=message)
"""
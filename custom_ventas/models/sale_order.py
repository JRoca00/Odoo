# -*- coding: utf-8 -*-
from odoo import models, fields, api

class WizardSale(models.TransientModel):
    _name = 'wizard.sale'

    partner_id = fields.Many2one('res.partner', string='Cliente')
    product_id = fields.Many2one('product.product', string='Producto')


    def action_print(self):
        print("kkkk---->", self.read()[0])
        data = {
            'model': 'wizard.sale',
            'form': self.read()[0]
        }
        print("Data", data)
        return self.env.ref('custom_ventas.report_appointment').report_action(self, data=data)


    def create_appointment(self):
        vals = {
            'partner_id': self.partner_id.id,
            'product_id': self.product_id.id,
        }
        self.patient_id.message_post(body="Test string ", subject="Appointment Creation")
        new_appointment = self.env['wizard.sale'].create(vals)
        context = dict(self.env.context)
        context['form_view_initial_mode'] = 'edit'
        return {'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'wizard.sale',
                'res_id': new_appointment.id,
                'context': context
                }
























"""from odoo import models, fields, api
from odoo.http import request

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    order_line_partner = fields.One2many('sale.order.partner', 'order_id', readonly="False")






class SaleOrderPartner(models.Model):
    _name = 'sale.order.partner'

    order_id = fields.Many2one('sale.order')
    product_id = fields.Many2one('product.product', string='Producto')
    description = fields.Text(string='Descripción')
    partner_id = fields.Many2one('res.partner', string='Proveedor')
"""






"""
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    partner_id = fields.Many2one('res.partner', string='Proveedor')



class SaleOrder(models.Model):
    
    _inherit = 'sale.order'

    mi_pestaña_pedidos = fields.One2many('sale.order.line', 'order_id', string='Mi Pestaña de Pedidos', editable=True)

"""
"""@api.onchange('order_line')
    def _onchange_order_line(self):
        self.mi_pestaña_pedidos = self.order_line"""
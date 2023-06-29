# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AccountMove(models.Model):

    _inherit = 'account.move'



    @api.onchange("currency_id")
    @api.depends('invoice_line_ids',"tax_totals_json")
    def update_price_quetzal(self):
        swap = 0
        if self.currency_id.id == 163:
            currency_ids = self.env['res.currency'].search([('id', '=', 2)],limit=1)
            for linea in currency_ids:
                for rate in linea.rate_ids:
                    swap = rate.inverse_company_rate
            for line in self.invoice_line_ids.price_unit:
                line.write({"price_unit": round(line.price_unit * swap,2)})

                












    """@api.onchange('currency_id')
    def _onchange_currency_id(self):
        temp_lines = []
        if self.currency_id.id == 163:
            currency_ids = self.env['res.currency'].search([('id', '=', 2)],limit=1)
            for linea in currency_ids:
                for rate in linea.rate_ids:
                    swap = rate.inverse_company_rate
            for line in self.invoice_line_ids:
                line_vals = {
                    'move_id': self.id,
                   # 'prduct_id': self.product_id,
                    'name': line.name,
                    'quantity': line.quantity,
                    'price_unit': line.price_unit * swap,
                    #'currency_id': self.currency_id,
                }
                self.line_ids.unlink()
                self.invoice_line_ids += self.env['account.move.line'].create(line_vals)
"""


 
    """@api.onchange('currency_id')
    def _onchange_currency_id(self,vals):
        converted_lines = []
        if self.currency_id.id == 163:
            currency_ids = self.env['res.currency'].search([('id', '=', 2)],limit=1)
            for linea in currency_ids:
                for rate in linea.rate_ids:
                    swap = rate.inverse_company_rate
        if 'currency_id' in vals:
            for line in self.invoice_line_ids:
                converted_lines.append((0, 0, {
                'name': line.name,
                'quantity': line.quantity,
                'price_unit': line.price_unit * 8,
                'account_id': line.account_id.id,
            }))
            res = super(AccountMove, self).write(vals)
            if 'currency_id' in vals:
                self.write({'invoice_line_ids': [(5, 0, 0)]})
                self.write({'invoice_line_ids': converted_lines})
            return res
"""








    """@api.onchange('currency_id')
    @api.depends('invoice_line_ids','tax_totals_json','price_subtotal')
    def update(self):
        for line in self.invoice_line_ids:
            line.price_unit = self.currency_id._convert(line.price_unit * 8, self.currency_id, self.company_id, self.date)
        self._compute_amount()"""
     
     
     
                
               
"""swap = 0
        if self.currency_id.id == 163:
            currency_ids = self.env['res.currency'].search([('id', '=', 2)],limit=1)
            for linea in currency_ids:
                for rate in linea.rate_ids:
                    swap = rate.inverse_company_rate"""               
               
               
               
               
               
               
               
     
""" lineas_actualizadas.append({''move_id': self.id,'product_id': line.product_id, 'name': line.name, 'quantity': line.quantity, 'price_unit': line.price_unit * swap, 'tax_ids': line.tax_ids, 'price_subtotal': line.price_subtotal})
                new_invoice_line_vals = {
                    'move_id': self.id,
                    'product_id': line.product_id, 
                    'name': line.name, 
                    'quantity': line.quantity, 
                    'price_unit': line.price_unit * swap, 
                    'tax_ids': line.tax_ids, 
                    'price_subtotal': line.price_subtotal,
                }
            #self.line_ids.unlink()
            new_invoice_line = self.invoice_line_ids.write(new_invoice_line_vals)"""
            
"""def funcion_onchange(self):
                nueva_linea = self.env['account.move.line'].new({
                    'move_id': self.id,
                    'name': 'Descripción de la nueva línea de factura',
                    'quantity': 1,
                    'price_unit': 100,
                    'tax_ids': [(6, 0, self.env.ref('impuesto_id').ids)],
                })
                self.invoice_line_ids += nueva_linea"""
            
#line.write({'product_id': 2})
            #self.line_ids.create(lineas_actualizadas)
                #line.write({lineas_actualizadas})
            
                
                
"""line.write({'product_id': line.product_id, 'name': line.name, 'quantity': line.quantity, 'price_unit': line.price_unit, 'tax_ids': line.tax_ids, 'price_subtotal': line.price_subtotal})
                line.invoice_line_ids.unlink()
                rewrite_all=[{'product_id': line.product_id, 'name': line.name, 'quantity': line.quantity, 'price_unit': line.price_unit * swap, 'tax_ids': line.tax_ids, 'price_subtotal': line.price_subtotal}]
                line.invoice_line_ids.create(rewrite_all)"""
                
                #line.write({"price_unit": line.price_unit * swap})
                

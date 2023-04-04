# -*- coding: utf-8 -*-
from odoo import models, fields, api
import json

class AccountMove(models.Model):
    
    _inherit = 'account.move'

    @api.onchange('currency_id')
    @api.depends('invoice_line_ids',"tax_totals_json")
    def update(self):
        swap = 0
        if self.currency_id.id == 163:
            currency_ids = self.env['res.currency'].search([('id', '=', 2)],limit=1)
            for linea in currency_ids:
                for rate in linea.rate_ids:
                    swap = rate.inverse_company_rate
            for line in self.invoice_line_ids:
                line.write({"price_unit": line.price_unit * swap})
                

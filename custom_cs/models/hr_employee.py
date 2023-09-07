# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.http import request
from odoo.exceptions import ValidationError

sig = 0

class ResConfigSettings(models.TransientModel):
    
    _inherit = 'res.config.settings' 

    cod_emp = fields.Integer("Código Inicial")

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('custom_cs.cod_emp', self.cod_emp)

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res['cod_emp'] = int(self.env['ir.config_parameter'].sudo().get_param('custom_cs.cod_emp', default=0))
        return res

class HrEmployee(models.Model): 
    _inherit = 'hr.employee'

    #codigo_empleado = fields.Char(string='Codigo de empleado') #borrar esta linea en produccion

    def update_codigo_empleado(self):
        cod_emp = self.env['res.config.settings'].sudo().get_values().get('cod_emp')
        sig = cod_emp + 1
        for employee in self:
            existing_record = self.search([('barcode', '=', cod_emp)])
            if existing_record and existing_record[0] != employee:
                existing_employee = existing_record[0]
                raise ValidationError(f"Código de empleado {cod_emp} ya está asignado a {existing_employee.name}.")
            employee.barcode = cod_emp
            employee.codigo_empleado = cod_emp
            employee.pin = cod_emp
            self.env['ir.config_parameter'].set_param('custom_cs.cod_emp', sig)





"""    @api.constrains('barcode')
    def update_codigo_empleado(self):
        cod_emp = self.env['res.config.settings'].sudo().get_values().get('cod_emp') #jale el 25
        sig = cod_emp + 1
        for employee in self:
            employee.codigo_empleado = cod_emp
            employee.pin = cod_emp
            employee.barcode = cod_emp
            self.env['ir.config_parameter'].set_param('custom_cs.cod_emp', sig)"""



# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions


class ProductTemplate(models.Model):
    _inherit = 'product.template'


    modelo = fields.Char(string='Modelo')
    estilo = fields.Char(string='Estilo')
 
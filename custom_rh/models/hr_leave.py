# -*- coding: utf-8 -*-
from odoo import models, fields


class HrLeaveType(models.Model):
    _inherit = 'hr.leave.type'

    code = fields.Char('Código de Nómina')
from odoo import models, fields


class AccountMove(models.Model):

    _inherit = 'account.move'


    enable_project = fields.Boolean("Gasto de Proyecto", default=False)
    project_data = fields.Many2one("project.project", "Proyectos")


class ProjectProject(models.Model):

    _inherit = 'project.project'
    
    invoice_project = fields.One2many('account.move','project_data', string='Facturas')
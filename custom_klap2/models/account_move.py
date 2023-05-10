from odoo import models, fields


class AccountMove(models.Model):

    _inherit = 'account.move'

    enable_project = fields.Boolean("Asociar a Proyecto", default=False)
    project_id = fields.Many2one("project.project", "Proyecto")


class ProjectProject(models.Model):

    _inherit = 'project.project'
    
    invoices_project = fields.One2many('account.move','project_id', string='Facturas')

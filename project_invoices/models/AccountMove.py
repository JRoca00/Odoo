from odoo import models, fields, api


class AccountMove(models.Model):

    _inherit = 'account.move'


    enable_project = fields.Boolean("Gasto de Proyecto", default=False)
    project_data = fields.Many2one("project.project", "Proyectos")


class ProjectProject(models.Model):

    _inherit = 'project.project'
    
    invoice_difference = fields.Monetary(string='Diferencia de Facturas', compute='_compute_invoice_difference')

    customer_invoices = fields.One2many(
        'account.move',
        'project_data',
        string='F. Cliente ',
        domain=[('move_type', '=', 'out_invoice')]
    )

    supplier_invoices = fields.One2many(
        'account.move',
        'project_data',
        string='F. Proveedor',
        domain=[('move_type', '=', 'in_invoice')]
    )

    def _compute_invoice_difference(self):
        for project in self:
            total_customer_invoices = sum(move.amount_total_signed for move in project.customer_invoices)
            total_supplier_invoices = sum(move.amount_total_signed for move in project.supplier_invoices)
            project.invoice_difference = total_customer_invoices + total_supplier_invoices
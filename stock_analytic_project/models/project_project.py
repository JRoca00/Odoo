from odoo import models, fields, api
from datetime import date
import logging

_logger = logging.getLogger(__name__)


class ProjectProject(models.Model):
    _inherit = 'project.project'

    customer_invoices = fields.Float(string="Customer")
    supplier_invoices = fields.Float(string="Supplier")
    stock_move = fields.Float(string="Stock Move")
    total_hours = fields.Float(string="Hours")
    utility = fields.Float(string="Utility", compute='_compute_utility', store=True)
    closed = fields.Boolean(string="Closed", default=False)
    account_move_close = fields.Many2one('account.move', string="Account Move")
    labour_amount_crm = fields.Float(string="Mano de Obra")
    materials_amount_crm = fields.Float(string="Materiales")
    expenses_amount_crm = fields.Float(string="Gastos")
    por_labour_crm_project = fields.Float()
    por_materials_crm_project = fields.Float()
    por_expense_crm_project = fields.Float()


    def create_account_move_for_pickings(self):
        partner_id = self.partner_id.id
        analytic_distribution = {str(self.analytic_account_id.id): 100}
        picking_ids = self.env['stock.picking'].search([('project_id', '=', self.id)])
        invoices_lines_ids = self.env['account.move.line'].search([('analytic_distribution','=', analytic_distribution)])
        move_line_vals = []
        journal_id = 0
        total_cost_picking = 0
        total_cost_invoicing = 0
        credit_account_id = 0
        debit_account_id = 0

        total_cost_invoicing = sum(self.env['account.move.line'].search([
                            ('analytic_distribution', '=', analytic_distribution),
                            ('move_id.move_type', '=', 'in_invoice')  # Assuming 'out_invoice' is used for customer invoices
                        ]).mapped('debit'))

        total_cost_picking = sum(move_line.product_id.standard_price * move_line.qty_done
                      for picking in self.env['stock.picking'].search([('project_id', '=', self.id)])
                      for move in picking.move_ids
                      for move_line in move.move_line_ids)
        
        #realice el search para proyectos con horas y lo cargue a la suma del cierre de obra final
        total_hours_planning = sum(self.env['planning.slot'].search([('project_id', '=', self.id)]).mapped('c_total'))
        
        
        if picking_ids:
            for picking in picking_ids:
                for move in picking.move_ids: 
                    for move_line in move.move_line_ids:
                        product_category = move_line.product_id.categ_id
                        if product_category.property_stock_account_output_categ_id:
                            credit_account_id = product_category.property_stock_account_output_categ_id.id
                            debit_account_id = product_category.property_account_income_categ_id.id
                            journal_id = product_category.property_stock_journal.id


        total_cost = total_cost_picking + total_cost_invoicing + total_hours_planning

        # Credito
        move_line_vals.append((0, 0, {
            'name': 'Cierre de proyecto ' + self.name,
            'partner_id': partner_id,
            'credit': total_cost,
            'account_id': credit_account_id,
            'analytic_distribution': analytic_distribution,
        }))

        # Debito
        move_line_vals.append((0, 0, {
            'name': 'Cierre de proyecto ' + self.name,
            'partner_id': partner_id,
            'debit': total_cost,
            'account_id': debit_account_id,
            'analytic_distribution': analytic_distribution,
        }))

        # Asiento Contable
        account_move = self.env['account.move'].create({
            'ref': 'Cierre de proyecto ' + self.name,
            'partner_id': partner_id,
            'date': date.today(),
            'journal_id': journal_id,
            'line_ids': move_line_vals,
        })

        account_move.action_post()
        self.closed = True
        self.account_move_close = account_move.id

    def calculate_utility(self):
        analytic_distribution = {str(self.analytic_account_id.id): 100}

        total_customer = sum(self.env['account.move.line'].search([
                            ('analytic_distribution', '=', analytic_distribution),
                            ('move_id.move_type', '=', 'out_invoice')  # Assuming 'out_invoice' is used for customer invoices
                        ]).mapped('credit'))

        total_supplier = sum(self.env['account.move.line'].search([
                            ('analytic_distribution', '=', analytic_distribution),
                            ('move_id.move_type', '=', 'in_invoice')  # Assuming 'out_invoice' is used for customer invoices
                        ]).mapped('debit'))

        total_stock = sum(move_line.product_id.standard_price * move_line.qty_done
                      for picking in self.env['stock.picking'].search([('project_id', '=', self.id)])
                      for move in picking.move_ids
                      for move_line in move.move_line_ids)
        
        
        total_hours_planning = sum(self.env['planning.slot'].search([('project_id', '=', self.id)]).mapped('c_total'))
        
        labour_amount_crm_search = sum(self.env['crm.lead'].search([('project_id', '=', self.id)]).mapped('labour_amount'))
        materials_amount_crm_search = sum(self.env['crm.lead'].search([('project_id', '=', self.id)]).mapped('materials_amount'))
        expenses_amount_crm_search = sum(self.env['crm.lead'].search([('project_id', '=', self.id)]).mapped('expenses_amount'))
        
        por_labour = (total_hours_planning / labour_amount_crm_search)
        por_materials = (total_stock / materials_amount_crm_search)
        por_expense = (total_supplier / expenses_amount_crm_search)
        
        self.por_labour_crm_project = por_labour
        self.por_materials_crm_project = por_materials
        self.por_expense_crm_project = por_expense
        self.labour_amount_crm = labour_amount_crm_search
        self.materials_amount_crm = materials_amount_crm_search
        self.expenses_amount_crm = expenses_amount_crm_search
        self.total_hours = total_hours_planning * -1
        self.customer_invoices = total_customer
        self.supplier_invoices = total_supplier * -1
        self.stock_move = total_stock * -1
        self.utility = total_customer + (self.stock_move + self.supplier_invoices + self.total_hours)

    @api.depends('customer_invoices', 'supplier_invoices', 'stock_move')
    def _compute_utility(self):
        for record in self:
            utility = record.stock_move - record.supplier_invoices + record.customer_invoices
            record.utility = utility
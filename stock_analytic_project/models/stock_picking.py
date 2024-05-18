from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = "stock.picking"

    project_id = fields.Many2one('project.project', string="Project", required=False)
    account_project2 = fields.Many2one('account.account')

    

    def button_validate(self):
        self = self.with_context(validate_analytic=True)
        return super().button_validate()


    

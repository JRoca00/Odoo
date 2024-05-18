from odoo import api, models


class StockMove(models.Model):
    _name = "stock.move"
    _inherit = ["stock.move", "analytic.mixin"]

    def _prepare_account_move_line(
        self, qty, cost, credit_account_id, debit_account_id, svl_id, description
    ):
        self.ensure_one()
        res = super(StockMove, self)._prepare_account_move_line(
            qty, cost, credit_account_id, debit_account_id, svl_id, description
        )
        if not self.analytic_distribution:
            return res
        for line in res:
            if (
                line[2]["account_id"]
                != self.product_id.categ_id.property_stock_valuation_account_id.id
            ):
                line[2].update({"analytic_distribution": self.analytic_distribution})
        return res

    def _prepare_procurement_values(self):
        res = super()._prepare_procurement_values()
        if self.analytic_distribution:
            res.update(
                {
                    "analytic_distribution": self.analytic_distribution,
                }
            )
        return res

    def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
        res = super()._prepare_move_line_vals(
            quantity=quantity, reserved_quant=reserved_quant
        )
        if self.analytic_distribution:
            res.update({"analytic_distribution": self.analytic_distribution})
        return res

    def _action_done(self, cancel_backorder=False):
        for move in self:
            if move.location_id.usage not in (
                "internal",
                "transit",
            ) or move.location_dest_id.usage in ("internal", "transit"):
                continue
            move._validate_distribution(
                **{
                    "product": move.product_id.id,
                    "business_domain": "stock_move",
                    "company_id": move.company_id.id,
                }
            )
        return super()._action_done(cancel_backorder=cancel_backorder)


class StockMoveLine(models.Model):
    _name = "stock.move.line"
    _inherit = ["stock.move.line", "analytic.mixin"]

    @api.model
    def _prepare_stock_move_vals(self):
        res = super()._prepare_stock_move_vals()
        if self.analytic_distribution:
            res.update({"analytic_distribution": self.analytic_distribution})
        return res

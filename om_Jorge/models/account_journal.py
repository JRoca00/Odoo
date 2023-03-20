# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AccountJournal(models.Model):
    
    
    _inherit = 'account.journal'
    
    is_credit_payment = fields.Boolean('Credito')
    product_id = fields.Many2one('product.template',"Producto")
                            #   (modelo que se busca, nombre que se muestra)





class AccountPayment(models.Model):
    
    
    _inherit = 'account.payment'
    
    
    sale_id = fields.Many2one('sale.order',"Pedido de Venta")
    reason_payment_account = fields.Many2one('reason.payment',"Motivo de Pago")
    charge = fields.Float('Recargo', readonly=True )#, compute="_calculado", store=True
    v_contado = fields.Float('Precio de Contado')
    visible =fields.Boolean('Visible', compute='_is_visible', store=True)
    payment_quotes = fields.Selection(
        string="Plazos de Pago",
        selection=[
            ('1',"1"),
            ('3',"3"),
            ('6',"6"),
            ('10',"10"),
            ('12',"12"),
            ('15',"15"),
            ('18',"18"),
        ],
    )
   


    @api.depends('v_contado','payment_quotes','amount')
    def calculado(self):
        if self.payment_quotes == '1':
            self.charge  = self.v_contado * 0.08
            self.amount = self.charge + self.v_contado
        if self.payment_quotes == '3':
            self.charge = self.v_contado * 0.12
            self.amount = self.charge + self.v_contado
        if self.payment_quotes == '6':
            self.charge = self.v_contado * 0.13
            self.amount = self.charge + self.v_contado
        if self.payment_quotes == '10':
            self.charge = self.v_contado * 0.15
            self.amount = self.charge + self.v_contado
        if self.payment_quotes == '12':
            self.charge = self.v_contado * 0.18
            self.amount = self.charge + self.v_contado
        if self.payment_quotes == '15':
            self.charge = self.v_contado * 0.20
            self.amount = self.charge + self.v_contado
        if self.payment_quotes == '18':
            self.charge = self.v_contado * 0.23
            self.amount = self.charge + self.v_contado

        

    @api.depends("journal_id")
    def _is_visible(self):  
        for record in self:
            if record.journal_id.is_credit_payment: 
                record.visible = True
            else:
                record.visible = False



"""class ReasonPayment(models.Model):
    
    
    _inherit = 'account.payment'
    
    
    mostrar =fields.Boolean('Mostrar', compute='_mostrar', store=True)
    reason_payment = fields.Selection(
        string="Motivo de Pago",
        selection=[
            ('Cheque',"Cheque"),
            ('Anticipo',"Anticipo"),
            ('Transferencia',"Transferencia"),
        ],
    )
    
    
    @api.depends("journal_id")
    def _mostrar(self):  
        for record in self:
            if record.journal_id.is_credit_payment: 
                record.mostrar = False
            else:
                record.mostrar = True
                """
                
                
class ReasonPayment(models.Model):
    
    _name = 'reason.payment'
    _description = 'Razon de pago'
    
    name = fields.Char(string='Motivo de Pago')

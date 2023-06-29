# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AccountJournal(models.Model):
    
    
    _inherit = 'account.journal'
    
    is_credit_payment = fields.Boolean('Credito')
    product_id = fields.Many2one('product.template',"Producto")
                            #   (modelo que se busca, nombre que se muestra)





class AccountPayment(models.Model):
    
    
    _inherit = 'account.payment'
    
    
    prueba= fields.One2many('reason.payment','pruebamany2one', string='Prueba')
    sale_id = fields.Many2one('sale.order',"Pedido de Venta")
    reason_payment_account = fields.Many2one('reason.payment',"Motivo de Pago")
    charge = fields.Float('Recargo', readonly=True )
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


    @api.onchange("sale_id")
    def _onchange(self):
        self.ref = self.sale_id.name


    @api.depends("reason_payment_account","prueba")
    def add_customer_to_lines(self):
        
        if self.prueba:
            self.prueba.unlink()
        if not self.reason_payment_account:
            return False
        for line in self.prueba:
            if line.name == self.reason_payment_account.name:
                return {
                    'warning': {
                        'title': "Valor existente",
                        'message': "El valor seleccionado ya se encuentra en la lista de valores."
                    }
                }
        else: line_values = {
            'id': self.reason_payment_account.id,
            'name' : self.reason_payment_account.name,
            'descri': self.reason_payment_account.descri,
            'pruebamany2one': self.reason_payment_account.pruebamany2one,
        }
        self.prueba |= self.prueba.new(line_values)
        return True

class ReasonPayment(models.Model):
    
    _name = 'reason.payment'
    _description = 'Razon de pago'
    
    name = fields.Char(string='Motivo de Pago')
    descri = fields.Integer(string='Precio')
    pruebamany2one = fields.Many2one('account.payment',"pagos")


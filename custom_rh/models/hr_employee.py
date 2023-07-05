# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    vac = fields.Float('Total', compute='_compute_vac')


    def _compute_vac(self):
        leaves_ids = self.env['hr.leave'].search([("employee_id", "=", self.id),("holiday_status_id.code","=","VAC")])
        vacaciones_gozadas = 0
        for leave in leaves_ids:
            vacaciones_gozadas += leave.number_of_days
        for employee in self:
            fecha_inicio_contrato = False
            for contract in employee.contract_ids:
                if contract.date_start:
                    fecha_inicio_contrato = contract.date_start
                    break

            if fecha_inicio_contrato:
                fecha_actual = datetime.now().date()
                dias_transcurridos = (fecha_actual - fecha_inicio_contrato).days
                vac = ((dias_transcurridos / 360) * 15 ) - vacaciones_gozadas
                employee.vac = round(vac, 0) 
            else:
                employee.vac = 0.0




class HrEmployee(models.Model):
    _name = 'hr.employee.pres'
    _inherit = ['mail.thread']
    
    currency_id = fields.Many2one('res.currency', string='Currency')
    name = fields.Char(string='Nombre', readonly=True, default='/')
    employeeid = fields.Many2one('hr.employee',"Empleado")
    vac_employee = fields.Float(string='Vacaciones')
    average_salary = fields.Float(string='Salario Promedio')
    last_bono14 = fields.Date(string='Fecha Ultimo Bono 14')
    last_aguinaldo = fields.Date(string='Fecha Ultimo Aguinaldo')
    pending_salary = fields.Float(string="Salario Pendiente")
    days_lab = fields.Float(string="Days")
    days_b14 = fields.Float(string="Daysb14")
    days_agui = fields.Float(string="Daysagui")
    daily_average_field = fields.Float(string="Promedio Diario")
    reason = fields.Selection([
        ('Despido', 'Despido'),
        ('Renuncia', 'Renuncia'),
    ], string='Motivo')
    
    tot_indemnizacion = fields.Float("Total Indemnizacion")
    tot_bono14 = fields.Float("Total Bono 14")
    tot_aguinaldo = fields.Float("Total Aguinaldo")
    tot_vac = fields.Float("Total de vacaciones")
    total = fields.Float("Total Pendiente")
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('done', 'Hecho'),
    ], string='Estado', default='draft')
    
    
    @api.onchange('employeeid')
    def vacaciones(self):
        self.vac_employee = self.employeeid.vac
    
    def btn_done(self):
        self.state = 'done'
        message = '\u2003\u2003•\u2003Estado: Publicado'
        self.message_post(body=message)
        
        

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            employee = self.env['hr.employee'].browse(vals.get('employeeid'))
            name = f"Prestaciones {employee.name}"
            vals['name'] = name
        return super(HrEmployee, self).create(vals)

    def prestaciones_tot(self):
        
        if self.reason == 'Despido':
              #calculos basicos
            actually_date = datetime.now().date()
            daily_average = self.average_salary / 365
            self.daily_average_field = daily_average
            #Dias transcurridos desde inicio de contrato
            start_contract = False
            start_contract = self.employeeid.contract_ids.date_start
            days_contract = (actually_date - start_contract).days
            self.days_lab = days_contract
            #Calculos indemnizacion
            self.tot_indemnizacion = daily_average * days_contract
            #Calculos Bono14
            last_date_bono14 = False
            last_date_bono14 = self.last_bono14
            if last_date_bono14:
                dias_transcurridos = (actually_date - last_date_bono14).days
                self.days_b14 = dias_transcurridos
                sumabono14 = (dias_transcurridos * (self.average_salary-250))/365
                self.tot_bono14 = sumabono14
            #Calculos Aguinaldo
            last_date_aguinaldo = False
            last_date_aguinaldo = self.last_aguinaldo
            if last_date_aguinaldo:
                dias_transcurridos = (actually_date - last_date_aguinaldo).days
                self.days_agui = dias_transcurridos
                sumaaguinaldo = (dias_transcurridos * (self.average_salary-250))/365
                self.tot_aguinaldo = sumaaguinaldo       
            #Calculos vacaciones
            days_vac = False
            days_vac = self.vac_employee
            suma_vac = (self.average_salary/31)*days_vac
            self.tot_vac = suma_vac
            #Calculos Total a pagar
            self.total = self.tot_indemnizacion + self.tot_bono14 + self.tot_aguinaldo + self.tot_vac + self.pending_salary
            
        if self.reason == 'Renuncia':
            self.tot_indemnizacion = 0.00
            #calculos basicos
            actually_date = datetime.now().date()
            daily_average = self.average_salary / 365
            self.daily_average_field = daily_average
            #Dias transcurridos desde inicio de contrato
            start_contract = False
            start_contract = self.employeeid.contract_ids.date_start
            days_contract = (actually_date - start_contract).days
            self.days_lab = days_contract
            #Calculos Bono14
            last_date_bono14 = False
            last_date_bono14 = self.last_bono14
            if last_date_bono14:
                dias_transcurridos = (actually_date - last_date_bono14).days
                self.days_b14 = dias_transcurridos
                sumabono14 = (dias_transcurridos * (self.average_salary-250))/365
                self.tot_bono14 = sumabono14
            #Calculos Aguinaldo
            last_date_aguinaldo = False
            last_date_aguinaldo = self.last_aguinaldo
            if last_date_aguinaldo:
                dias_transcurridos = (actually_date - last_date_aguinaldo).days
                self.days_agui = dias_transcurridos
                sumaaguinaldo = (dias_transcurridos * (self.average_salary-250))/365
                self.tot_aguinaldo = sumaaguinaldo       
            #Calculos vacaciones
            days_vac = False
            days_vac = self.vac_employee
            suma_vac = (self.average_salary/31)*days_vac
            self.tot_vac = suma_vac
            #Calculos Total a pagar
            self.total = self.tot_indemnizacion + self.tot_bono14 + self.tot_aguinaldo + self.tot_vac + self.pending_salary
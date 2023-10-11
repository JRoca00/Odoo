# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime
from odoo.http import request
from odoo.exceptions import ValidationError

#Codigo asignacion de empleado

sig = 0

class ResConfigSettings(models.TransientModel):
    
    _inherit = 'res.config.settings' 

    cod_emp = fields.Integer("Código Inicial")

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('custom_cs.cod_emp', self.cod_emp)

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res['cod_emp'] = int(self.env['ir.config_parameter'].sudo().get_param('custom_cs.cod_emp', default=0))
        return res

class HrEmployee(models.Model): 
    _inherit = 'hr.employee'

    codigo_empleado = fields.Char(string='Codigo de empleado') #borrar esta linea en produccion

    def update_codigo_empleado(self):
        cod_emp = self.env['res.config.settings'].sudo().get_values().get('cod_emp')
        sig = cod_emp + 1
        for employee in self:
            existing_record = self.search([('barcode', '=', cod_emp)])
            if existing_record and existing_record[0] != employee:
                existing_employee = existing_record[0]
                raise ValidationError(f"Código de empleado {cod_emp} ya está asignado a {existing_employee.name}.")
            employee.barcode = cod_emp
            employee.codigo_empleado = cod_emp
            employee.pin = cod_emp
            self.env['ir.config_parameter'].set_param('custom_cs.cod_emp', sig)




#Codigo prestaciones
class HrEmployee(models.Model):
    _inherit = 'hr.leave'

    employee_vac = fields.Many2one('hr.employee.vac',"Empleado")



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



class HrEmployeeVac(models.Model):
    _name = 'hr.employee.vac'
    _inherit = ['mail.thread']
    
    employeeid = fields.Many2one('hr.employee',"Empleado")
    period = fields.Selection([
        ('2021-2022', '2021-2022'),
        ('2022-2023', '2022-2023'),
        ('2023-2024', '2023-2024'),
        ('todos', 'Todos'),
    ], string='Periodo', default='todos')
    tot_vac = fields.Float(string='Total Pendiente')
    vac_list = fields.One2many('hr.leave', 'employee_vac', string='Ausencias', compute='_compute_vac_list')
    vac = fields.Float('Total', compute='_compute_vac')
    name = fields.Char(string="Name", compute="_compute_name", store=True)

    state = fields.Selection([
            ('draft', 'Borrador'),
            ('done', 'Hecho'),
        ], string='Estado', default='draft')
        
        
    def btn_done(self):
        self.state = 'done'
        message = '\u2003\u2003•\u2003Estado: Publicado'
        self.message_post(body=message)

    @api.onchange('employeeid')
    def vacaciones(self):
        vac_dis = self.employeeid.vac
        salario = self.employeeid.contract_ids.wage
        self.tot_vac = (salario/31)*vac_dis


    @api.depends('employeeid', 'period')
    def _compute_vac_list(self):
        for record in self:
            # Borre el one2many para el onchange
            record.vac_list = [(5, 0, 0)]

            # LLeno el one2many
            ausencias = self.env['hr.leave']
            if record.employeeid:
                if record.period != 'todos':
                    ausencias = ausencias.search([
                        ('employee_id', '=', record.employeeid.id),
                        ('name', '=', record.period),  # filtro segun el perido
                        ('holiday_status_id.code', '=', 'VAC')  # Filtro segun el id de la ausencia
                    ])
                else:
                    ausencias = ausencias.search([
                        ('employee_id', '=', record.employeeid.id),
                        ('holiday_status_id.code', '=', 'VAC')  
                    ])
            for ausencia in ausencias:
                record.vac_list = [(4, ausencia.id, 0)]

    @api.depends('vac_list')
    def _compute_vac(self):
        for record in self:
            record.vac = sum(ausencia.number_of_days for ausencia in record.vac_list)

    @api.depends('employeeid', 'period')
    def _compute_name(self):
        for record in self:
            if record.employeeid:
                # Generar el campo name en el formato deseado con el correlativo
                record.name = f"VAC / {record.employeeid.name} / #{record.period}"
            else:
                record.name = False





"""    @api.depends('employeeid', 'period')
    def _compute_vac_list(self):
        for record in self:
            # Borramos los registros existentes en el campo One2many
            record.vac_list = [(5, 0, 0)]

            # Llenamos el campo One2many con las ausencias del empleado seleccionado
            ausencias = self.env['hr.leave']
            if record.employeeid:
                if record.period != 'todos':
                    ausencias = ausencias.search([
                        ('employee_id', '=', record.employeeid.id),
                        ('name', '=', record.period)  # Filtramos por el período seleccionado
                    ])
                else:
                    ausencias = ausencias.search([
                        ('employee_id', '=', record.employeeid.id)
                    ])
            for ausencia in ausencias:
                record.vac_list = [(4, ausencia.id, 0)]"""




"""    @api.depends('employeeid', 'period')
    def _compute_vac_list(self):
        for record in self:
            # Borramos los registros existentes en el campo One2many
            record.vac_list = [(5, 0, 0)]

            # Llenamos el campo One2many con las ausencias del empleado seleccionado
            if record.employeeid and record.period:
                ausencias = self.env['hr.leave'].search([
                    ('employee_id', '=', record.employeeid.id),
                    ('name', '=', record.period)  # Filtramos por el período seleccionado
                ])
                for ausencia in ausencias:
                    record.vac_list = [(4, ausencia.id, 0)]"""








"""    @api.depends('employeeid')
    def _compute_vac_list(self):
        for record in self:
            # Borramos los registros existentes en el campo One2many
            record.vac_list = [(5, 0, 0)]

            # Llenamos el campo One2many con las ausencias del empleado seleccionado
            if record.employeeid:
                ausencias = self.env['hr.leave'].search([('employee_id', '=', record.employeeid.id)])
                for ausencia in ausencias:
                    record.vac_list = [(4, ausencia.id, 0)]

    @api.depends('vac_list')
    def _compute_vac(self):
        for record in self:
            record.vac = sum(ausencia.number_of_days for ausencia in record.vac_list)
"""








"""@api.onchange('employeeid')
    def vacaciones(self):
        self.vac_employee = self.employeeid.vac"""


"""def _compute_vac(self):
        leaves_ids = self.env['hr.leave'].search([("employee_id", "=", self.id),("holiday_status_id.code","=","VAC")])
        vacaciones_gozadas = 0
        for leave in leaves_ids:
            vacaciones_gozadas += leave.number_of_days
            self.vac = vacaciones_gozadas"""
        

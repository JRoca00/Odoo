from odoo import models, fields, api
from datetime import datetime
from odoo.http import request
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError

#Codigo ingresar y guardar valores en la configuración para cod de empleado
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

    codigo_empleado = fields.Char(string='Codigo de empleado') #borrar esta linea en produccion para cassesa porque ya existe

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




#Código de calculo de vacaciones y agregar referencia de finiquito laboral y de vacaciones en la vista del empleado
class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    vac = fields.Float('Total', compute='_compute_vac')
    vac_list = fields.One2many('hr.employee.vac', 'employeeid')
    employee_fin = fields.Many2one('hr.employee.pres', compute='_compute_last_employee')


    def _compute_last_employee(self):
        for employee in self:
            fini = self.env['hr.employee.pres'].search([('employeeid', '=', employee.id)])
            self.employee_fin = fini.id


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


#Codigo prestaciones
class HrLeave(models.Model):
    _inherit = 'hr.leave'

    employee_vac = fields.Many2one('hr.employee.vac',"Empleado")


#Código de prestaciones Laborales
class HrEmployeePres(models.Model):
    _name = 'hr.employee.pres'
    _inherit = ['mail.thread']
    
    name = fields.Char(string="Name", compute="_compute_name", store=True)
    currency_id = fields.Many2one('res.currency', string='Currency')
    employeeid = fields.Many2one('hr.employee',"Empleado")
    vac_employee = fields.Float(string='Vacaciones')
    average_salary = fields.Float(string='Salario Promedio')
    last_bono14 = fields.Date(string='Fecha Ultimo Bono 14')
    last_aguinaldo = fields.Date(string='Fecha Ultimo Aguinaldo')
    pending_salary = fields.Float(string="Salario Pendiente")
    days_lab = fields.Float(string="Days")
    days_b14 = fields.Float(string="Daysb14")
    days_agui = fields.Float(string="Daysagui")
    sal_pen = fields.Float(string="Salario Pendiente")
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
    
    
    @api.depends('employeeid', 'reason')
    def _compute_name(self):
        for record in self:
            if record.employeeid:
                record.name = f"Finiquito / {record.employeeid.name} / {record.reason}"
            else:
                record.name = False


    @api.onchange('employeeid')
    def vacaciones(self):
        self.vac_employee = self.employeeid.vac
    
    def btn_done(self):
        self.state = 'done'
        message = '\u2003\u2003•\u2003Estado: Publicado'
        self.message_post(body=message)
        
        

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
            self.sal_pen = self.pending_salary
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
            self.sal_pen = self.pending_salary
            self.total = self.tot_indemnizacion + self.tot_bono14 + self.tot_aguinaldo + self.tot_vac + self.pending_salary


#Codigo de vacaciones
class HrEmployeeVac(models.Model):
    _name = 'hr.employee.vac'
    _inherit = ['mail.thread']
    
    employeeid = fields.Many2one('hr.employee',"Empleado")
    period = fields.Char(string='Periodo', default='Todos')
    tot_vac = fields.Float(string='Total a Pagar')
    vac_list = fields.One2many('hr.leave', 'employee_vac', string='Ausencias', compute='_compute_vac_list')
    vac = fields.Float('Total', compute='_compute_vac')
    name = fields.Char(string="Name", compute="_compute_name", store=True)
    create_date = fields.Datetime(string='Fecha de Creación', default=lambda self: fields.Datetime.now())

    state = fields.Selection([
            ('draft', 'Borrador'),
            ('done', 'Hecho'),
        ], string='Estado', default='draft')
        
        
    def btn_done(self):
        self.state = 'done'
        message = '\u2003\u2003•\u2003Estado: Publicado'
        self.message_post(body=message)



    @api.depends('employeeid', 'period')
    def _compute_vac_list(self):
        for record in self:
            # Borre el one2many para el onchange
            record.vac_list = [(5, 0, 0)]

            # LLeno el one2many
            ausencias = self.env['hr.leave']
            if record.employeeid:
                if record.period != 'Todos':
                    ausencias = ausencias.search([
                        ('employee_id', '=', record.employeeid.id),
                        ('name', '=', record.period),  # filtro segun el perido
                        ('holiday_status_id.code', '=', 'VAC')  # Filtro segun el id de la ausencia
                    ])
                    if not ausencias:  # Si no se encontraron coincidencias
                        raise UserError('No existen coincidencias en el período ingresado.')
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
            salario = self.employeeid.contract_ids.wage
            record.tot_vac = (salario/31)* record.vac


    @api.depends('employeeid', 'period')
    def _compute_name(self):
        for record in self:
            if record.employeeid:
                record.name = f"VAC / {record.employeeid.name} / {record.period}"
            else:
                record.name = False


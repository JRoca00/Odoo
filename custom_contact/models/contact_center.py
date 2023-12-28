# -*- coding: utf-8 -*-
from email.policy import default
from odoo import models, fields, api, exceptions
from odoo.http import request

class ContactCenter(models.Model):
    _name = 'contact.center'
    _inherit = ['mail.thread']
    _description = 'Contact Center'

    #Datos para Formulario
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('process', 'Proceso'),
        ('done', 'Finalizado'),
        ('cancel', 'Cancelado'),
    ], string='Estado', default='draft')


    #Variables del formulario
    name = fields.Char(string="Name", store=True)
    type = fields.Selection([
        ('ENT', 'Llamada Entrante'),
        ('SAL', 'Llamada Saliente'),
        ('WHA', 'WhatsApp'),
        ('AP', 'Atención Presencial'),
    ], string='Tipo de Llamada')
    employee_id = fields.Many2one('hr.employee',"Empleado")
    mobile_phone = fields.Char(string='Movil', related="employee_id.mobile_phone", readonly=False)
    project = fields.Char(string='Proyecto')
    #supervisor_id = fields.Many2one('hr.employee', related="employee_id.coach_id", string='Supervisor')
    boss_id = fields.Many2one('hr.employee',related="employee_id.parent_id", string='Jefe de Territorio')
    gestor = fields.Many2one('hr.employee', string='Gestor', domain="[('department_id', '=', 109)]")
    monto = fields.Float(string='Monto de Reclamos')
    create_date = fields.Datetime(string='Fecha de Creación', default=lambda self: fields.Datetime.now())
    process_date = fields.Datetime(string='Fecha en Proceso')
    done_date = fields.Datetime(string='Fecha Finalizado')
    diferencia_fechas = fields.Float(string='Diferencia de Fechas')
    diferencia_fechas_horas = fields.Float(string='Diferencia de Fechas')
    note = fields.Text('Nota de Descripción')
    notere = fields.Text('Nota de Resolución')
    tipo_solicitud_id = fields.Many2one('contact.center.tipo_solicitud', string='Tipo de Solicitud')
    subtipo_solicitud_id = fields.Many2one('contact.center.subtipo_solicitud', string='Subtipo de Solicitud', domain="[('tipo_id', '=', tipo_solicitud_id)]")
    tipologia_id = fields.Many2one('contact.center.tipologia', string='Tipología', domain="[('subtipo_id', '=', subtipo_solicitud_id)]")
    ticket_id = fields.Many2one('helpdesk.ticket', string='Ticket')
    visible =fields.Boolean('Visible', compute='_is_visible', store=True)


    @api.onchange('tipo_solicitud_id')
    def _onchange_tipo_solicitud(self):
        self.subtipo_solicitud_id = False

    @api.onchange('subtipo_solicitud_id')
    def _onchange_subtipo_solicitud(self):
        self.tipologia_id = False

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('contact.center')
        return super(ContactCenter, self).create(vals)


    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        self.mobile_phone = self.employee_id.mobile_phone
        #self.project = self.employee_id.partner_id.name
        self.boss = self.employee_id.parent_id.name

    

    @api.depends("tipo_solicitud_id")
    def _is_visible(self):  
        for record in self:
            if record.tipo_solicitud_id.monto_reclamo: 
                record.visible = True
            else:
                record.visible = False


    def btn_process(self):
        self.state = 'process'
        message = '\u2003\u2003•\u2003Estado: En Proceso'
        self.message_post(body=message)
        self.process_date = fields.Datetime.now()
    
    def btn_cancel(self):
        self.state = 'cancel'
        message = '\u2003\u2003•\u2003Estado: Cancelado'
        self.message_post(body=message)

    #metodo para no permitir que eliminen
    def unlink(self):
        for record in self:
            if record.state in ['draft', 'process','done','cancel']:  
                raise exceptions.UserError("No puedes eliminar un registro que ha sido ingresado.")
        return super(custom_contact, self).unlink()



    def btn_done(self):
        self.state = 'done'
        message = '\u2003\u2003•\u2003Estado: Terminado'
        self.message_post(body=message)
        self.done_date = fields.Datetime.now()

        for record in self:
            if record.done_date and record.create_date:
                fecha_creacion = fields.Datetime.from_string(record.create_date)
                fecha_finalizado = fields.Datetime.from_string(record.done_date)
                diferencia = (fecha_finalizado - fecha_creacion).total_seconds() / 3600
                hora = round(diferencia, 0)
                diferencia_dias = (fecha_finalizado - fecha_creacion).days
                record.diferencia_fechas = diferencia_dias
                record.diferencia_fechas_horas = hora

# Modelos de las tipologias
class TipoSolicitud(models.Model):
    _name = 'contact.center.tipo_solicitud'
    _inherit = ['mail.thread']

    name = fields.Char(string='Tipo Solicitud', required=True)
    monto_reclamo = fields.Boolean(string='Monto para Reclamo', default=False)
    subtipo_ids = fields.One2many('contact.center.subtipo_solicitud', 'tipo_id', string='Subtipos')

class SubtipoSolicitud(models.Model):
    _name = 'contact.center.subtipo_solicitud'
    _inherit = ['mail.thread']

    name = fields.Char(string='Sub-Tipo Solicitud', required=True)
    tipo_id = fields.Many2one('contact.center.tipo_solicitud', string='Tipo de Solicitud')
    tipologia_ids = fields.One2many('contact.center.tipologia', 'subtipo_id', string='Tipologías')

class Tipologia(models.Model):
    _name = 'contact.center.tipologia'
    _inherit = ['mail.thread']

    name = fields.Char(string='Tipología', required=True)
    subtipo_id = fields.Many2one('contact.center.subtipo_solicitud', string='Subtipo de Solicitud')

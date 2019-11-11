# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class HospitalAgrements(models.Model):
    _name = 'hospital.agreement'
    _description = 'Convenios'

    name = fields.Char(
        string='Nombre',
        size=64,
        required=False,
        readonly=False,
        )
    company_id = fields.Many2one(
        'res.company',
        string='Compañia',
    )
    services_company_id = fields.Many2one(
        'res.company',
        string='Compañia Servicios',
    )
    medicine_company_id = fields.Many2one(
        'res.company',
        string='Compañia Medicamentos',
    )
    medical_coverage = fields.Selection(
        [('mount','Monto'),('percent','Porcentaje')], 
        string='Covertura Medica', 
        default='mount'
    )
    amount = fields.Float(
        string="Monto/Porcentaje"
    )
    change_amount = fields.Boolean(
        string='Cambiar Valor',
        default=False
    )
    excluded_product_ids = fields.One2many(
        'excluded.product',
        'hospital_agreement_id',
        string='Productos Excluidos En Covertura Medica',
    )
    co_payment = fields.Boolean(
        string='CoPago',
        default=False
    )
    co_payment_amount = fields.Float(
        string="Monto Co-Pago"
    )
    price_list_id = fields.Many2one(
        'product.pricelist',
        string='Lista De Precios',
    )
    credit_limit = fields.Float(
        string='Limite De Credito',
    )
    description = fields.Text(
        string='Descripcion',
    )
    active = fields.Boolean(
        string='Activo',
        default=True
    )


class ExcludedProducts(models.Model):
    _name = 'excluded.product'
    _description = 'Productos Excluidos En Covertura Medica'

    name = fields.Many2one(
        'product.product',
        string='Producto',
    )
    hospital_agreement_id = fields.Many2one(
        'hospital.agreement',
        string='Convenio ID',
    )

class acsHospitalization(models.Model):
    _inherit = 'acs.hospitalization'

    agreement_id = fields.Many2one(
        'hospital.agreement',
        string='Convenio',
    )
    policy = fields.Char(
        string='Nº Poliza/RFC',
    )
    co_payment = fields.Boolean(
        string='CoPago',
        default=False,
        related="agreement_id.co_payment"
    )
    co_payment_amount = fields.Float(
        string="Monto Co-Pago"
    )
    amount = fields.Float(
        string="Monto/Porcentaje"
    )
    total_patient = fields.Float(
        string='Total Paciente',
        compute="compute_totals"
    )
    total_agreement = fields.Float(
        string='Total Convenio',
        compute="compute_totals"
    )
    amount_total = fields.Float(
        string='Total',
        compute="compute_totals"
    )
    deposit = fields.Float(
        string='Deposito',
    )
    medical_coverage = fields.Selection(
        [('mount','Monto'),('percent','Porcentaje')], 
        string='Covertura Medica', 
        default='mount',
        related="agreement_id.medical_coverage"
    )

    @api.onchange('agreement_id')
    def onchange_agreement_id(self):
        if self.agreement_id:
            self.co_payment_amount = self.agreement_id.co_payment_amount
            self.amount = self.agreement_id.amount

    @api.one
    def compute_totals(self):
        ampat = 0
        amagree = 0
        total = 0
        for x in self.consumable_line:
            ampat += x.patient_amount
            amagree += x.agreement_amount
            total += x.subtotal
        self.total_patient = ampat
        self.total_agreement = amagree
        self.amount_total = total


    
class hmsAppointment(models.Model):
    _inherit = 'hms.appointment'

    agreement_id = fields.Many2one(
        'hospital.agreement',
        string='Convenio',
    )
    policy = fields.Char(
        string='Nº Poliza/RFC',
    )
    co_payment = fields.Boolean(
        string='CoPago',
        default=False,
        related="agreement_id.co_payment"
    )
    co_payment_amount = fields.Float(
        string="Monto Co-Pago"
    )
    amount = fields.Float(
        string="Monto/Porcentaje"
    )
    total_patient = fields.Float(
        string='Total Paciente',
        compute="compute_totals"
    )
    total_agreement = fields.Float(
        string='Total Convenio',
        compute="compute_totals"
    )
    amount_total = fields.Float(
        string='Total',
        compute="compute_totals"
    )
    deposit = fields.Float(
        string='Deposito',
    )
    medical_coverage = fields.Selection(
        [('mount','Monto'),('percent','Porcentaje')], 
        string='Covertura Medica', 
        default='mount',
        related="agreement_id.medical_coverage"
    )
    services_line = fields.One2many(
        'appointment.consumable.service',
        'appointment_id',
        string='Services',
    )
    @api.multi
    def create_account(self):
        self.ensure_one()
        partner_id = self.env['res.partner'].search([('name', '=', self.patient_id.name)],limit=1)       
        account=self.env['account.invoice'].create({
            'partner_id':partner_id.id,
            'origin':self.name,
          
           })
        if account:
            line = []
            for x in self.consumable_line:
                account_line=self.env['account.invoice.line'].create({                            
                    'origin':self.name,
                    'invoice_id':account.id,
                    'product_id':x.product_id.id,
                    'name':self.product_id.name,
                    #'display_type':,
                    'company_id':self.company_id.id,
                    'account_id':30,
                    #'account_analytic_id':,
                    #'analytic_tag_ids':,
                    'quantity':x.qty,
                    'uom_id':x.product_id.uom_id.id,
                    'price_unit':x.price_unit,
                    #'discount':,
                    #'invoice_line_tax_ids':,
                    'price_subtotal':x.subtotal,
                    'price_total':x.price_unit,
                    #'currency_id':,
                    })
                line.append(account_line)
            print("*************************",line)
            cr = self.env.cr
            sql ="select id from account_account where company_id='"+str(self.agreement_id.services_company_id.id)+"' limit 1"
            cr.execute(sql)
            account_ids = cr.fetchone()
            account_id=account_ids[0]
            cr = self.env.cr
            sql2 ="select id from account_journal where company_id='"+str(self.agreement_id.services_company_id.id)+"' limit 1"
            cr.execute(sql2)
            journal_ids = cr.fetchone()
            journal_id=journal_ids[0]
            cr = self.env.cr
            sql3 ="select commercial_partner_id from res_partner where name='"+str(self.patient_id.name)+"' limit 1"
            cr.execute(sql3)
            partner_comers = cr.fetchone()
            partner_comer=partner_comers[0]
            cr = self.env.cr
            sql4 ="select id from stock_warehouse where company_id='"+str(self.agreement_id.services_company_id.id)+"' limit 1"
            cr.execute(sql4)
            wares = cr.fetchone() 
            ware=wares[0]          
            print("*****************************",account_id,journal_id,partner_comer,ware)
            cr = self.env.cr
            cr.execute("update account_invoice set account_id='"+str(account_id)+"',journal_id='"+str(journal_id)+"',company_id='"+str(self.agreement_id.services_company_id.id)+"',commercial_partner_id='"+str(partner_comer)+"',warehouse_id='"+str(ware)+"'  where id='"+str(account.id)+"' ")
            
            if line:
                for l in line:
                    cr = self.env.cr
                    cr.execute("update account_invoice_line set account_id='"+str(account_id)+"',company_id='"+str(self.agreement_id.services_company_id.id)+"'  where invoice_id='"+str(account.id)+"' ")
        self.factura_product()  


    @api.multi
    def factura_product(self):
        partner_id = self.env['res.partner'].search([('name', '=', self.patient_id.name)],limit=1)       
        account=self.env['account.invoice'].create({
            'partner_id':partner_id.id,
            'origin':self.name,
          
           })
        if account:
            line = []
            for x in self.consumable_line:
                account_line=self.env['account.invoice.line'].create({                            
                    'origin':self.name,
                    'invoice_id':account.id,
                    'product_id':x.product_id.id,
                    'name':self.product_id.name,
                    #'display_type':,
                    'company_id':self.company_id.id,
                    'account_id':30,
                    #'account_analytic_id':,
                    #'analytic_tag_ids':,
                    'quantity':x.qty,
                    'uom_id':x.product_id.uom_id.id,
                    'price_unit':x.price_unit,
                    #'discount':,
                    #'invoice_line_tax_ids':,
                    'price_subtotal':x.subtotal,
                    'price_total':x.price_unit,
                    #'currency_id':,
                    })
                line.append(account_line)
            print("*************************",line)
            cr = self.env.cr
            sql ="select id from account_account where company_id='"+str(self.agreement_id.medicine_company_id.id)+"' limit 1"
            cr.execute(sql)
            account_ids = cr.fetchone()
            account_id=account_ids[0]
            cr = self.env.cr
            sql2 ="select id from account_journal where company_id='"+str(self.agreement_id.medicine_company_id.id)+"' limit 1"
            cr.execute(sql2)
            journal_ids = cr.fetchone()
            journal_id=journal_ids[0]
            cr = self.env.cr
            sql3 ="select commercial_partner_id from res_partner where name='"+str(self.patient_id.name)+"' limit 1"
            cr.execute(sql3)
            partner_comers = cr.fetchone()
            partner_comer=partner_comers[0]
            cr = self.env.cr
            sql4 ="select id from stock_warehouse where company_id='"+str(self.agreement_id.medicine_company_id.id)+"' limit 1"
            cr.execute(sql4)
            wares = cr.fetchone() 
            ware=wares[0]          
            print("*****************************",account_id,journal_id,partner_comer,ware)
            cr = self.env.cr
            cr.execute("update account_invoice set account_id='"+str(account_id)+"',journal_id='"+str(journal_id)+"',company_id='"+str(self.agreement_id.medicine_company_id.id)+"',commercial_partner_id='"+str(partner_comer)+"',warehouse_id='"+str(ware)+"'  where id='"+str(account.id)+"' ")
            
            if line:
                for l in line:
                    cr = self.env.cr
                    cr.execute("update account_invoice_line set account_id='"+str(account_id)+"',company_id='"+str(self.agreement_id.medicine_company_id.id)+"'  where invoice_id='"+str(account.id)+"' ")
           
                

       

    @api.onchange('agreement_id')
    def onchange_agreement_id(self):
        if self.agreement_id:
            self.co_payment_amount = self.agreement_id.co_payment_amount
            self.amount = self.agreement_id.amount

    @api.one
    def compute_totals(self):
        ampat = 0
        amagree = 0
        total = 0
        for x in self.consumable_line:
            ampat += x.patient_amount
            amagree += x.agreement_amount
            total += x.subtotal
        self.total_patient = ampat
        self.total_agreement = amagree
        self.amount_total = total


class AppointmentCosumable(models.Model):
    _inherit = 'appointment.consumable'

    price_unit = fields.Float(
        string='Unit Price',
    )
    subtotal = fields.Float(
        string="Subtotal"
    )
    agreement_amount = fields.Float(
        string='Monto Convenio',
    )
    patient_amount = fields.Float(
        string='Monto Paciente',
    )
    type = fields.Selection([
        ('consu', 'Consumable'),
        ('service', 'Service')], string='Product Type', related="product_id.product_tmpl_id.type")

    @api.onchange('product_id','price_unit','qty')
    def onchange_products_agreement(self):
        self.price_unit = self.product_id.product_tmpl_id.list_price
        self.subtotal = self.product_id.product_tmpl_id.list_price * self.qty
        if self.appointment_id.agreement_id:
            if self.appointment_id.medical_coverage == 'percent':
                self.agreement_amount = self.subtotal * (self.appointment_id.amount/100)
            else:
                if self.appointment_id.amount > self.subtotal:
                    self.agreement_amount = self.subtotal
                else:
                    self.agreement_amount = self.appointment_id.amount
        self.patient_amount = self.subtotal - self.agreement_amount

class AppointmentCosumable(models.Model):
    _inherit = 'consumable.line'

    price_unit = fields.Float(
        string='Unit Price',
    )
    subtotal = fields.Float(
        string="Subtotal"
    )
    agreement_amount = fields.Float(
        string='Monto Convenio',
    )
    patient_amount = fields.Float(
        string='Monto Paciente',
    )
    type = fields.Selection([
        ('consu', 'Consumable'),
        ('service', 'Service')], string='Product Type', related="product_id.product_tmpl_id.type")

    @api.onchange('product_id','price_unit','qty')
    def onchange_products_agreement(self):
        self.price_unit = self.product_id.product_tmpl_id.list_price
        self.subtotal = self.product_id.product_tmpl_id.list_price * self.qty
        if self.hospitalization_id.agreement_id:
            if self.hospitalization_id.medical_coverage == 'percent':
                self.agreement_amount = self.subtotal * (self.hospitalization_id.amount/100)
            else:
                if self.hospitalization_id.amount > self.subtotal:
                    self.agreement_amount = self.subtotal
                else:
                    self.agreement_amount = self.hospitalization_id.amount
        self.patient_amount = self.subtotal - self.agreement_amount


class ACSAppointmentConsumableService(models.Model):
    _name = "appointment.consumable.service"
    _description = "List of services"

    name = fields.Char(string='Name',default=lambda self: self.product_id.name)
    product_id = fields.Many2one('product.product', ondelete="cascade", string='Consumable')
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure', help='Amount of medication (eg, 250 mg) per dose')
    qty = fields.Float(string='Quantity', default=1.0)
    appointment_id = fields.Many2one('hms.appointment', ondelete="restrict", string='Hospitalization')
    move_id = fields.Many2one('stock.move', string='Stock Move')
    date = fields.Date("Consumed Date", default=fields.Date.context_today)
    price_unit = fields.Float(
        string='Unit Price',
    )
    subtotal = fields.Float(
        string="Subtotal"
    )
    agreement_amount = fields.Float(
        string='Monto Convenio',
    )
    patient_amount = fields.Float(
        string='Monto Paciente',
    )

    @api.onchange('product_id')
    def onchange_product(self):
        if self.product_id:
            self.product_uom = self.product_id.uom_id.id

    @api.onchange('product_id','price_unit','qty')
    def onchange_products_agreement(self):
        self.price_unit = self.product_id.product_tmpl_id.list_price
        self.subtotal = self.product_id.product_tmpl_id.list_price * self.qty
        if self.appointment_id.agreement_id:
            if self.appointment_id.medical_coverage == 'percent':
                self.agreement_amount = self.subtotal * (self.appointment_id.amount/100)
            else:
                if self.appointment_id.amount > self.subtotal:
                    self.agreement_amount = self.subtotal
                else:
                    self.agreement_amount = self.appointment_id.amount
        self.patient_amount = self.subtotal - self.agreement_amount
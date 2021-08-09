from odoo import models, fields, api


class LP_Crm(models.Model):
  _inherit = 'crm.lead'
  lp_company_id = fields.Many2one('res.partner', 'company' , compute = '_compute_company')
  lp_individual_id = fields.Many2many('res.partner')
  lp_OneDrive_url = fields.Char('OneDrive folder URL')
  lp_client_size = fields.Char('Size of the client')
  lp_industry = fields.Selection([('Automobiles_and_Components', 'Automobiles and Components'),
                                  ('banks', 'Banks'),
                                  ('Capital_Goods', 'Capital Goods'),
                                  ('Commercial_Professional_Services', 'Commercial and Professional Services'),
                                  ('Consumer_Durables_Apparel', 'Consumer Durables and Apparel'),
                                  ('Consumer_Services', 'Consumer Services'),
                                  ('Diversified_Financials', 'Diversified Financials'),
                                  ('energy', 'Energy'),
                                  ('Food_Beverage_Tobacco', ' Food, Beverage, and Tobacco'),
                                  ('Food_Staples_Retailing', 'Food and Staples Retailing'),
                                  ('Health_Care_Equipment_Services', ' Health Care Equipment and Services'),
                                  ('Household_Personal_Products', ' Household and Personal Products'),
                                  ('Hospitality', 'Hospitality'),
                                  ('insurance', 'Insurance'),
                                  ('materials', 'Materials'),
                                  ('logistics', 'Logistics'),
                                  ('Media_Entertainment', 'Media and Entertainment'),
                                  ('Pharmaceuticals_Biotechnology_LifeSciences', 'Pharmaceuticals, Biotechnology, and Life Sciences'),
                                  ('Real_Estate', 'Real Estate'),
                                  ('retailing', 'Retailing'),
                                  ('Semiconductors_Semiconductor_Equipment', ' Semiconductors and Semiconductor Equipment'),
                                  ('Software_Services', 'Software and Services'),
                                  ('Technology_Hardware_Equipment', 'Technology Hardware and Equipment'),
                                  ('Telecommunication_Services', 'Telecommunication Services'),
                                  ('transportation', 'Transportation'),
                                  ('travel', 'Travel'),
                                  ('utilities', 'Utilities'),
                                  ('travel', 'Travel'),
                                  ('others', 'Others')
                                  ],
                                 'Indusrty', default="others")
  lp_country = fields.Many2one('res.country','country')
  lp_channel_source = fields.Char('Channel From')
  lp_others = fields.Text('Others Information') #description
  contact_other_info = fields.Text('Others') #description
  lp_opportunity = fields.Selection([('new', 'New'),
                              ('Existing', 'Existing (e.g. CR)'),
                              ('outsourcing_contracts', 'Outsourcing contracts'),
                              ('maintenance', 'Maintenance')],
                             'Opportunity Type', default="new")
  lp_budget = fields.Char('Do they have budget for this opportunity?')
  lp_budget_authority = fields.Char(' Authority to use budget')
  lp_start_date = fields.Datetime('Start Date')
  lp_end_date = fields.Datetime('Finsh Date')
  lp_dept_head = fields.Many2one('res.users', string='Department head', domain=lambda self: [('id', 'in', self.env.ref('lp_crm.lp_group_crm_dept_head').users.ids)])
  lp_director = fields.Many2one('res.users', string='Director', domain=lambda self: [('id', 'in', self.env.ref('lp_crm.lp_group_crm_director').users.ids)])
  lp_go_ahead = fields.Boolean('GoAhead')
  lp_stage_name = fields.Char(related="stage_id.name", string='Stage Name')
  lp_director_viewer = fields.Boolean(compute='_driector_approve_viewer')
  stage_id = fields.Many2one(
      'crm.stage', string='Stage', index=True, tracking=True,
      compute='_compute_stage_id', readonly=False, store=True,
      copy=False, group_expand='_read_group_stage_ids', ondelete='restrict',
      domain="['|', ('team_id', '=', False), ('team_id', '=', team_id)]")
  @api.constrains('lp_start_date', 'lp_end_date')
  def check_dates(self):
        if self.lp_start_date and self.lp_end_date:
            if self.lp_start_date > self.lp_end_date:
                raise UserError('The date from cannot be greater than date to')
  @api.depends('partner_id')
  def _compute_company(self):
      self.lp_company_id = self.partner_id

  @api.depends('lp_director')
  def _driector_approve_viewer(self):
      if self.env.user.id == self.lp_director.id:
          self.lp_director_viewer = True
      else:
          self.lp_director_viewer = False


  def Director_approver(self):
      self.ensure_one()
      is_da = self.env.user.id in self.env.ref('lp_crm.lp_group_crm_director').users.ids
      if is_da and self.env.user.id == self.lp_director.id:
        if self.lp_go_ahead==False:
          self.lp_go_ahead = True
        stage_presentation = self.env['crm.stage'].sudo().search([('name', '=', 'Presentation')])
        if stage_presentation:
         self.stage_id = stage_presentation[0].id


  def notify_dept_head(self):
      marketing_head=self.env['hr.department'].sudo().search([('name','=','Marketing')])
      support_head = self.env['hr.department'].sudo().search([('name', '=', 'Support')])
      notification_marketing= [(0, 0, {
              'res_partner_id': marketing_head.manager_id.user_id.partner_id.id,
              'notification_type': 'inbox'
          })]
      notification_support= [(0, 0, {
              'res_partner_id': support_head.manager_id.user_id.partner_id.id,
              'notification_type': 'inbox'
          })]
      notification_delivery = [(0, 0, {
              'res_partner_id': self.lp_dept_head.partner_id.id,
              'notification_type': 'inbox'
          })]

      self.message_post(
              body='Opportunity won:          ' + str(self.name) +'-'
                   +str(self.company_id.name) +'                                        '+'    Dears, ' +'We would like to inform you that the opportunity '
                   +str(self.name)+
                   ' - '
                   +str(self.company_id.name) +
                   ' is won.                regards',              message_type="notification",
              author_id=self.env.user.partner_id.id,
              notification_ids=notification_delivery)
      self.message_post(
              body='Opportunity won:          ' + str(self.name) +'-'
                   +str(self.company_id.name) +'                                        '+'    Dears, ' +'We would like to inform you that the opportunity '
                   +str(self.name)+
                   ' - '
                   +str(self.company_id.name) +
                   ' is won.                regards',              message_type="notification",

              author_id=self.env.user.partner_id.id,
              notification_ids=notification_support)
      self.message_post(
              body='Opportunity won:          ' + str(self.name) +'-'
                   +str(self.company_id.name) +'                                        '+'    Dears, ' +'We would like to inform you that the opportunity '
                   +str(self.name)+
                   ' - '
                   +str(self.company_id.name) +
                   ' is won.                regards',              message_type="notification",
              author_id=self.env.user.partner_id.id,
              notification_ids=notification_marketing)


  @api.onchange('stage_id')
  def onchange_stage_id(self):
          if self.lp_go_ahead==True:
              self.lp_stage_name = 'Won'

  def write(self, vals):
      if self.stage_id.name=='Won':
       self.notify_dept_head()

      res = super(LP_Crm, self).write(vals)
      return res
class LP_contact(models.Model):
  _inherit = 'res.partner'


class LP_stages(models.Model):
  _inherit = 'crm.stage'

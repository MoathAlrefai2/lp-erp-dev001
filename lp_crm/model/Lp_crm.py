from odoo import models, fields, api


class LP_Crm(models.Model):
  _inherit = 'crm.lead'


  lp_company_id = fields.Many2one('res.partner', 'company')#, domain="[('company_type', '=', 'company')]")#,domain="[('company_type', '=', 'company')]")
  #, domain="[('state', '=', 'Current')]")
  lp_individual_id = fields.Many2many('res.partner')#, domain="[('lp_type', '=', 'lp_person')]")
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

  @api.onchange('lp_opportunity')
  def compute_going(self):
      self.ensure_one()
      #is_admin = self.env.user.has_group('base.user_admin')
      is_dh = self.env.user.id in self.env.ref('lp_crm.lp_group_crm_director').users.ids
      if is_dh and self.env.user.id == self.lp_director.id:
          if self.lp_opportunity == 'new':
             self.lp_go_ahead = True
          else:
              self.lp_go_ahead =False

  def notify_dept_head(self):
      marketing_head=self.env['hr.department'].sudo().search([('name','=','Marketing')])
      Support_head = self.env['hr.department'].sudo().search([('name', '=', 'Support')])
      notification_marketing= [(0, 0, {
              'res_partner_id': marketing_head.manager_id.user_id.partner_id.id,
              'notification_type': 'inbox'
          })]
      notification_support= [(0, 0, {
              'res_partner_id': Support_head.manager_id.user_id.partner_id.id,
              'notification_type': 'inbox'
          })]
      #marketing_head.manager_id.user_id.partner_id.id
      notification_delivery = [(0, 0, {
              'res_partner_id': self.lp_dept_head.partner_id.id,
              'notification_type': 'inbox'
          })]
      print('osama')
      self.message_post(
              body='Opportunity is Won!! ',
              message_type="notification",
              author_id=self.env.user.partner_id.id,
              notification_ids=notification_delivery)
      self.message_post(
              body='Opportunity is Won!! ',
              message_type="notification",
              author_id=self.env.user.partner_id.id,
              notification_ids=notification_support)
      self.message_post(
              body='Opportunity is Won!! ',
              message_type="notification",
              author_id=self.env.user.partner_id.id,
              notification_ids=notification_marketing)

  def write(self, vals):
      if self.stage_id.name=='Won':
       self.notify_dept_head()

      res = super(LP_Crm, self).write(vals)
      return res
class LP_contact(models.Model):
  _inherit = 'res.partner'



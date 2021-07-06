from odoo import models, fields, api


class LP_Crm(models.Model):
  _inherit = 'crm.lead'


  lp_company_id = fields.Many2one('res.partner', 'company', required=True)#, domain="[('company_type', '=', 'company')]")#,domain="[('company_type', '=', 'company')]")
  #, domain="[('state', '=', 'Current')]")
  lp_individual_id = fields.Many2many('res.partner', required=False)#, domain="[('lp_type', '=', 'lp_person')]")
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
  contact_other_info = fields.Text('Others:') #description
  lp_opportunity = fields.Selection([('new', 'New'),
                              ('Existing', 'Existing (e.g. CR)'),
                              ('outsourcing_contracts', 'Outsourcing contracts'),
                              ('maintenance', 'Maintenance')],
                             'Opportunity Type', default="new")
  lp_budget = fields.Char('Do they have budget for this opportunity?')
  lp_budget_authority = fields.Char(' Authority to use budget')
  lp_start_date = fields.Datetime('Start Date')
  lp_end_date = fields.Datetime('Finsh Date')
  lp_dept_head = fields.Many2one('res.partner', string='Department head')
  lp_go_ahead = fields.Boolean('Go Ahead',compute='compute_going')

  @api.onchange('lp_opportunity')
  def compute_going(self):
      self.lp_go_ahead = True if self.lp_opportunity == 'new' else False

  # def write(self, values):
  #     if self.stage_id.name =='Won':
  #        self.notify_message()
  #     return super(LP_Crm, self).write(values)
  #
  # def notify_message(self):
  #     notification_ids = [(0, 0, {
  #         'res_partner_id': self.user_id.partner_id.id,
  #         'notification_type': 'inbox'
  #     })]
  #     self.message_post(
  #         body='Opportunity is Won',
  #         message_type="notification",
  #         author_id=self.env.user.partner_id.id,
  #         notification_ids=notification_ids)
  # def create_qotation(self):
  #     action = self.env["ir.actions.actions"]._for_xml_id("sale_crm.sale_action_quotations_new")
  #     action['context'] = {
  #         'search_default_opportunity_id': self.id,
  #         'default_opportunity_id': self.id,
  #         'search_default_partner_id': self.partner_id.id,
  #         'default_partner_id': self.partner_id.id,
  #         'default_team_id': self.team_id.id,
  #         'default_campaign_id': self.campaign_id.id,
  #         'default_medium_id': self.medium_id.id,
  #         'default_origin': self.name,
  #         'default_source_id': self.source_id.id,
  #         'default_company_id': self.company_id.id or self.env.company.id,
  #         'default_tag_ids': [(6, 0, self.tag_ids.ids)]
  #     }
  #     return action
class LP_contact(models.Model):
  _inherit = 'res.partner'



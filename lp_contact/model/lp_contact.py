from odoo import models, fields, api


class LP_Contact(models.Model):
  _inherit = 'res.partner'
  lp_position = fields.Selection([('lp_decision_maker', 'Decision maker'),
                              ('lp_business_influencer', 'Business influencer'),
                              ('lp_technical_influencer', 'Technical influencer'),
                              ('lp_technical', 'Technical'),('lp_information_provider', 'Information provider')],
                            'Position', default="lp_technical")


  def write(self, values):
      try:
        if not values['name'].startswith("ind_"):
            values['name'] = 'ind_' + values['name']
      except:
          pass
      return super(LP_Contact, self).write(values)
  @api.model
  def create(self, values):
       values['name'] = 'ind_' + values['name']
       return super(LP_Contact, self).create(values)

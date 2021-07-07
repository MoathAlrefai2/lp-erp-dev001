from odoo import models, fields, api


class LP_Contact(models.Model):
  _inherit = 'res.partner'
  lp_position = fields.Selection([('lp_decision_maker', 'Decision maker'),
                              ('lp_business_influencer', 'Business influencer'),
                              ('lp_technical_influencer', 'Technical influencer'),
                              ('lp_technical', 'Technical'),('lp_information_provider', 'Information Provider')],
                            'Position', default="lp_technical")
  lp_label = fields.Char('label for name.', default='ind_',readonly=True)


  def write(self, values):
      prefix="ind_"
      try:
        if not values['name'].startswith(prefix):
            values['name'] = prefix + values['name']
      except:
          pass
      return super(LP_Contact, self).write(values)
  @api.model
  def create(self, values):
       prefix = "ind_"
       values['name'] = prefix + values['name']
       return super(LP_Contact, self).create(values)

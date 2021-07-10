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
      if self.company_type == 'person':
       try:
        if not self.name.startswith('ind_'):
            values['name'] = prefix + values['name']
            values['lp_label']=False
        else:
            values['lp_label'] = False
       except:
           pass
      return super(LP_Contact, self).write(values)

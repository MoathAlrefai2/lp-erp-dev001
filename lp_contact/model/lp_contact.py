from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class LP_Contact(models.Model):
  _inherit = 'res.partner'
  lp_position = fields.Selection([('lp_decision_maker', 'Decision maker'),
                              ('lp_business_influencer', 'Business influencer'),
                              ('lp_technical_influencer', 'Technical influencer'),
                              ('lp_technical', 'Technical'),('lp_information_provider', 'Information Provider')],
                            'Position', default="lp_technical")
  lp_label_name = fields.Char('label for name.', default='ind_',readonly=True)
  lp_name = fields.Char('name label')

  def get_prefix_person(self,values):
      prefix = "ind_"
      try:
              values['lp_name'] = prefix + values['name']
      except Exception as e:
          _logger.exception(e)
      return values
  def write(self, values):
    if self.company_type == 'person':
         values = self.get_prefix_person(values)
    else:
         values['lp_name'] = self.name
    return super(LP_Contact, self).write(values)

  @api.model
  def create(self, values):
        if values['company_type'] == 'person':
            values = self.get_prefix_person(values)
        else:
            values['lp_name'] = self.name
        return super(LP_Contact, self).create(values)
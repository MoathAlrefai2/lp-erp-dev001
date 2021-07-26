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
  lp_name = fields.Char('name label') #create new field to show the name without prefix ("ind_")


  def write(self, values):
    prefix="ind_"
    try:
      if self.company_type == 'person':
        if not self.name.startswith('ind_'):
            values['lp_name'] = prefix + values['name']
        else:
            values['lp_name'] =  values['name']
      else:
          values['lp_name'] = values['name']
    except Exception as e:
         _logger.exception(e)

    return super(LP_Contact, self).write(values)

  @api.model
  def create(self, values):
        prefix = "ind_"
        try:
            if  values['company_type'] == 'person':
               values['lp_name'] = prefix + values['name']
            else:
                values['lp_name'] = values['name']
        except Exception as e:
             _logger.exception(e)

        return super(LP_Contact, self).create(values)
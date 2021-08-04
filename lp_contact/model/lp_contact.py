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
  lp_name = fields.Char('name label',compute='onchange_name')


  @api.depends('lp_name')
  def onchange_name(self):
      prefix = "ind_"
      if self.company_type == 'person':
       self.lp_name = prefix + self.name
      else:
        self.lp_name = self.name

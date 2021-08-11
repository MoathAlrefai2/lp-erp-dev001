from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class LP_Contact(models.Model):
  _inherit = 'res.partner'
  lp_label_name = fields.Char('label for name.', default='ind_',readonly=True)
  lp_name = fields.Char('name label',compute='onchange_name')
  lp_position = fields.Many2many('hr.job')


  @api.depends('lp_name')
  def onchange_name(self):
      prefix = "ind_"
      if self.company_type == 'person':
       self.lp_name = prefix + self.name
      else:
        self.lp_name = self.name

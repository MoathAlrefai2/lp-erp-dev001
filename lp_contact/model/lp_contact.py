from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class LP_Contact(models.Model):
  _inherit = 'res.partner'
  lp_label_name = fields.Char('label for name.', default='ind_',readonly=True)
  lp_name = fields.Char('name label',compute='onchange_name')
  lp_position = fields.Many2many('hr.job')

  @api.onchange('lp_position')
  def onchange_create_position(self):
      lp_decision_maker = self.env['hr.job'].sudo().search([('name', '=', 'Decision maker')])
      lp_business_influencer = self.env['hr.job'].sudo().search([('name', '=', 'Business influencer')])
      lp_technical_influencer = self.env['hr.job'].sudo().search([('name', '=', 'Technical influencer')])
      lp_Technical = self.env['hr.job'].sudo().search([('name', '=', 'Technical')])
      lp_information_provider = self.env['hr.job'].sudo().search([('name', '=', 'Information Provider')])
      if not lp_decision_maker:
          self.env['hr.job'].create({'name': 'Decision maker'})
      if not lp_business_influencer:
          self.env['hr.job'].create({'name': 'Business influencer'})
      if not lp_technical_influencer:
          self.env['hr.job'].create({'name': 'Technical influencer'})
      if not lp_Technical:
          self.env['hr.job'].create({'name': 'Technical'})
      if not lp_information_provider:
          self.env['hr.job'].create({'name': 'Information Provider'})

  @api.depends('lp_name')
  def onchange_name(self):
      prefix = "ind_"
      if self.company_type == 'person':
       self.lp_name = prefix + self.name
      else:
        self.lp_name = self.name

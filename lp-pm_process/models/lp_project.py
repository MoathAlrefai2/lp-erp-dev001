# -*- coding: utf-8 -*-

from odoo import models, fields, api


class LP_Project(models.Model):
    _inherit = 'project.project'

    type = fields.Selection(
        [('fixed_time_price', 'Fixed Time/Price'),
         ('change_request', 'Change Request'),
         ('outsourcing', 'Outsourcing'),
         ('Inhouse', 'Inhouse')],
        'Type', default="fixed_time_price")

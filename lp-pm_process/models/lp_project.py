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

    member_ids = fields.Many2many('res.partner', string='Team Members')
    teams_link = fields.Char('TEAMS Channel')
    devops_link = fields.Char('DevOps Project')
    status = fields.Selection(
        [('new', 'New'),
         ('in_progress', 'In Progress'),
         ('closed', 'Closed')],
        'Status', default="new")


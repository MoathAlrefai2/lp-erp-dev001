# -*- coding: utf-8 -*-

from odoo import models, fields, api


class LP_Project(models.Model):
    _inherit = 'project.project'

    lp_type = fields.Selection(
        [('lp_fixed_time_price', 'Fixed Time/Price'),
         ('lp_change_request', 'Change Request'),
         ('lp_outsourcing', 'Outsourcing'),
         ('lp_Inhouse', 'Inhouse')],
        'Type', default="lp_fixed_time_price")

    lp_member_ids = fields.Many2many('res.partner', string='Team Members')
    lp_teams_link = fields.Char('TEAMS Channel')
    lp_devops_link = fields.Char('DevOps Project')
    lp_status = fields.Selection(
        [('lp_new', 'New'),
         ('lp_in_progress', 'In Progress'),
         ('lp_closed', 'Closed')],
        'Status', default="lp_new")

    lp_budget = fields.Char('Budget')
    lp_date_end = fields.Date('End Date')
    lp_department_head = fields.Many2one('res.users', string='Department Head')


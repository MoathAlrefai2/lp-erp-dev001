# -*- coding: utf-8 -*-

from odoo import models, fields, api


class LP_Project(models.Model):
    _inherit = ['project.project']

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

    lp_budget = fields.Char('Budget', readonly=True, tracking=True)
    date_start = fields.Date(readonly=True, tracking=True)
    lp_date_end = fields.Date('End Date', readonly=True, tracking=True)
    lp_department_head = fields.Many2one('res.users', string='Department Head')

    lp_proposed_budget = fields.Char('Proposed Budget', tracking=True)
    lp_proposed_date_start = fields.Date('Proposed Start Date', tracking=True)
    lp_proposed_date_end = fields.Date('Proposed End Date', tracking=True)


    def approve_proposed_values(self):
        self.ensure_one()
        #self.message_post(body=msg, subject='Reminder',subtype='mt_comment')
        self.lp_budget = self.lp_proposed_budget
        self.date_start = self.lp_proposed_date_start
        self.lp_date_end = self.lp_proposed_date_end
        self.lp_proposed_budget = ''
        self.lp_proposed_date_start = ''
        self.lp_proposed_date_end = ''
        #Log the change into history


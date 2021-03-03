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

    lp_budget = fields.Char('Budget', readonly=True)
    lp_date_end = fields.Date('End Date', readonly=True)
    lp_department_head = fields.Many2one('res.users', string='Department Head')

    lp_proposed_budget = fields.Char('Proposed Budget')
    lp_proposed_date_start = fields.Date('Proposed Start Date')
    lp_proposed_date_end = fields.Date('Proposed End Date',)


    #def pick_one(self):
    #    """ This method used to customize display name of the record """
    #    result = []
    #    for record in self:
    #        rec_name = "%s (%s)" % (record.name, record.date_start)
    #        result.append((record.id, rec_name))
    #    return result


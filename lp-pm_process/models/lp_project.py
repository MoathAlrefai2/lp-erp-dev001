# -*- coding: utf-8 -*-
#import logging
from urllib.parse import urlparse
from odoo import models, fields, api
from odoo.exceptions import AccessError, ValidationError

#_logger = logging.getLogger(__name__)

class LP_Project(models.Model):
    _inherit = ['project.project']

    lp_type = fields.Selection([('lp_fixed_time_price', 'Fixed Time/Price'),
         ('lp_change_request', 'Change Request'),
         ('lp_outsourcing', 'Outsourcing'),
         ('lp_Inhouse', 'Inhouse')],
        'Type', default="lp_fixed_time_price")

    lp_member_ids = fields.Many2many('res.partner', string='Team Members')
    lp_teams_link = fields.Char('TEAMS Channel')
    lp_devops_link = fields.Char('DevOps Project')
    lp_status = fields.Selection([('lp_new', 'New'),
         ('lp_in_progress', 'In Progress'),
         ('lp_closed', 'Closed')],
        'Status', default="lp_new")

    lp_budget = fields.Char('Budget', readonly=True, tracking=True)
    date_start = fields.Date(readonly=True, tracking=True)
    lp_date_end = fields.Date('End Date', readonly=True, tracking=True)
    lp_approver = fields.Many2one('res.users', string='Approver (Dept. Head)', domain=lambda self: [('id', 'in', self.env.ref('lp-pm_process.lp_group_project_approver').users.ids)], tracking=True)

    lp_proposed_budget = fields.Char('Proposed Budget', tracking=True)
    lp_proposed_date_start = fields.Date('Proposed Start Date', tracking=True)
    lp_proposed_date_end = fields.Date('Proposed End Date', tracking=True)


    #DevOps fields
    lp_devops_token = fields.Char('Token')
    lp_devops_org_url = fields.Char('Organization URL', readonly=True)
    lp_devops_project_name = fields.Char('Project Name', readonly=True)


    @api.constrains('lp_devops_link')
    def _check_lp_devops_link(self):
        for record in self:
            if record.lp_devops_link:
                tmp_parsed_url = urlparse(record.lp_devops_link)
                tmp_path_parts = tmp_parsed_url.path.strip("/").split("/")
                if len(tmp_path_parts) != 2 or tmp_parsed_url.scheme == '' or tmp_parsed_url.netloc == '':
                    raise ValidationError('DevOps Project URL format is not valid. The valid format: http(s)://{domain}/{organization}/{project}')
                else:
                    record.lp_devops_org_url = tmp_parsed_url.scheme + "://" + tmp_parsed_url.netloc + "/" + tmp_path_parts[0]
                    record.lp_devops_project_name = tmp_path_parts[1]
            else:
                record.lp_devops_org_url = ""
                record.lp_devops_project_name = ""


    def approve_proposed_values(self):
        self.ensure_one()

        is_admin = self.env.user.has_group('base.user_admin') #self.env.user.id in self.env.ref('base.user_admin').users.ids
        is_dh = self.env.user.id in self.env.ref('lp-pm_process.lp_group_project_approver').users.ids

        #_logger.info('is_admin: %s',is_admin)
        #_logger.info('is_dh: %s',is_dh)
        #_logger.info('self_lp_approver_id: %s',self.lp_approver.id)
        #_logger.info('self_env_user_id: %s',self.env.user.id)
        #_logger.warning('len(tmp_path_parts): %s',len(tmp_path_parts))

        if is_admin or (is_dh and self.env.user.id == self.lp_approver.id):
            #self.message_post(body=msg, subject='Reminder',subtype='mt_comment')
            self.lp_budget = self.lp_proposed_budget
            self.date_start = self.lp_proposed_date_start
            self.lp_date_end = self.lp_proposed_date_end
            self.lp_proposed_budget = ''
            self.lp_proposed_date_start = ''
            self.lp_proposed_date_end = ''
            #Log the change into history
        else:
            raise AccessError('Only Admin or project\'s DH can approve the change')
        

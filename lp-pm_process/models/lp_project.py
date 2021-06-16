# -*- coding: utf-8 -*-
#import logging
from urllib.parse import urlparse
from odoo import models, fields, api
from odoo.exceptions import AccessError, ValidationError

#sudo pip3 install vsts
from vsts.vss_connection import VssConnection

#sudo pip3 install msrest
from msrest.authentication import BasicAuthentication
from vsts.work_item_tracking.v4_1.models.wiql import Wiql

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

    # method notify_update to send notification from PM TO Dp head
    def notify_dept_head(self, message):
        notification_ids = [(0, 0, {
            'res_partner_id': self.lp_approver.partner_id.id,
            'notification_type': 'inbox'
        })]
        self.message_post(
            body='Values proposed by ' + str(self.user_id.partner_id.name) + " :" + message + "need approval",
            message_type="notification",
            author_id=self.env.user.partner_id.id,
            notification_ids=notification_ids)

    # write method (when click save call notify_update)
    def write(self, vals):
        message = ""
        flag = False
        if 'lp_proposed_budget' in vals:
            message = message + "Proposed budget (" + str(vals['lp_proposed_budget']) + ") "
            flag = True
        if 'lp_proposed_date_start' in vals:
            message = message + "Proposed Start Date (" + str(vals['lp_proposed_date_start']) + ") "
            flag = True
        if 'lp_proposed_date_end' in vals:
            message = message + "Proposed End Date (" + str(vals['lp_proposed_date_end']) + ") "
            flag = True
        if flag:
            self.notify_dept_head(message)
        res = super(LP_Project, self).write(vals)
        return res
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
        
    #def emit(msg, *args):
    #    #print(msg % args)
    #    _logger.warning(msg % args)


    #def print_work_item(work_item):
    #    emit(
    #    "{0} {1}: {2}".format(
    #        work_item.fields["System.WorkItemType"],
    #        work_item.id,
    #        work_item.fields["System.Title"],
    #    ))

    def sync_devops_task(self, devops_task, odoo_task):
        # do nothing
        odoo_task.lp_devops_ref_id = devops_task.id


    def devops_sync(self):
        self.ensure_one()
        personal_access_token = self.lp_devops_token
        organization_url = self.lp_devops_org_url
        project_name = self.lp_devops_project_name

        if (not personal_access_token) or (not organization_url) or (not project_name):
            raise ValidationError('Please check you DevOps token and DevOps project URL')

        credentials = BasicAuthentication('', personal_access_token)
        connection = VssConnection(base_url=organization_url, creds=credentials)
        wiql = Wiql(query=f"""select [System.Id] From WorkItems Where [System.WorkItemType] = 'Task' AND [System.TeamProject] = '{project_name}' order by [System.Id] desc""")

        wit_client = connection.get_client('vsts.work_item_tracking.v4_1.work_item_tracking_client.WorkItemTrackingClient')
        wiql_results = wit_client.query_by_wiql(wiql).work_items

        if wiql_results:
            # WIQL query gives a WorkItemReference with ID only
            # => we get the corresponding WorkItem from id

            tasks_to_be_synced = []
            #odoo_tasks = self.env['project.task']
            odoo_task_ids = self.env['project.task'].search([('project_id', '=', self.id)]).ids
            for task in self.env['project.task'].browse(odoo_task_ids):
                if task.lp_devops_ref_id: #odoo task already connected to devops task
                    work_item = wit_client.get_work_item(int(task.lp_devops_ref_id))
                    self.sync_devops_task(work_item, task)
                    tasks_to_be_synced.append(task.lp_devops_ref_id)

            tasks_to_be_inserted = [wit_client.get_work_item(int(tmp_devops_task.id)) for tmp_devops_task in wiql_results if tmp_devops_task.id not in tasks_to_be_synced]
            for work_item in tasks_to_be_inserted:
                #print_work_item(work_item)
                #_logger.warning("{0} {1}: {2}".format(
                #    work_item.fields["System.WorkItemType"],
                #    work_item.id,
                #    work_item.fields["System.Title"]))
                tmp_description = ''
                if "System.Description" in work_item.fields:
                    tmp_description = work_item.fields["System.Description"]

                tmp_task = {
                    'name': work_item.fields["System.Title"],
                    'description': tmp_description,
                    'project_id': self.id,
                    'lp_devops_ref_id': work_item.id
                    }
                self.env['project.task'].create(tmp_task)


            #work_items = (wit_client.get_work_item(int(res.id)) for res in wiql_results)
            #for work_item in work_items:
                ##print_work_item(work_item)
                #_logger.warning("{0} {1}: {2}".format(
                    #work_item.fields["System.WorkItemType"],
                    #work_item.id,
                    #work_item.fields["System.Title"]))



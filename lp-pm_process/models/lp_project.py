# -*- coding: utf-8 -*-
import logging
from urllib.parse import urlparse
from odoo import models, fields, api
from odoo.exceptions import AccessError, ValidationError

#sudo pip3 install vsts
from vsts.vss_connection import VssConnection
from datetime import  datetime

#sudo pip3 install msrest
from msrest.authentication import BasicAuthentication
from vsts.work_item_tracking.v4_1.models.wiql import Wiql

_logger = logging.getLogger(__name__)

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
    def notify_send_mail(self):
        mail_lp = self.env['mail.mail']
        values = {}
        values.update({'subject': ' proposed Values'})
        values.update({'email_to': self.lp_approver.login})
        values.update({'body_html': 'body'})
        values.update({'body': 'Values proposed need approval'})
        msg_id = mail_lp.create(values)
        if msg_id:
           mail_lp.send([msg_id])

    def notify_dept_head(self, message):
        if self.lp_proposed_budget or self.lp_proposed_date_start or self.lp_proposed_date_end:
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
            self.notify_send_mail()
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
            if self.lp_proposed_budget or self.lp_proposed_date_start or self.lp_proposed_date_end:
               self.lp_budget = self.lp_proposed_budget
               self.date_start = self.lp_proposed_date_start
               self.lp_date_end = self.lp_proposed_date_end
            self.lp_proposed_budget = ''
            self.lp_proposed_date_start = ''
            self.lp_proposed_date_end = ''
            #Log the change into history
        else:
            raise AccessError('Only Admin or project\'s DH can approve the change')


    def insert_task(self,work_item):
        tmp_task = self.get_task(work_item)
        tmp_tags = self.get_tags(work_item)
        insert_counter = 0
        record = self.env['project.task'].create(tmp_task)
        insert_counter = insert_counter + 1
        try:
            if tmp_tags:
                record.tag_ids = tmp_tags
        except:
            _logger.error('ERROR: tag has a problem on this task!')
        return insert_counter
    def update_task(self,work_item,task):
        tmp_task = self.get_task(work_item)#tmp_task
        tmp_tags = self.get_tags(work_item)#tmp_tags
        update_counter=0
        if "System.ChangedDate" in work_item.fields:
            if task.lp_devops_changed_date != tmp_task.get('lp_devops_changed_date'):
             update_counter= update_counter+1
             task.write(tmp_task)
             try:

                if tmp_tags:
                    task.tag_ids = tmp_tags
             except:
                _logger.error('ERROR: tag has a problem on this task!')
        return update_counter
    def get_tags(self,work_item):
        tmp_tags = []
        if "System.Tags" in work_item.fields:
            tags = work_item.fields["System.Tags"]
            if tags:
                tags = tags.split("; ")
                for tag in tags:
                    lp_s = self.env['project.tags'].search([('name', '=', tag)])
                    if not lp_s:
                        self.env['project.tags'].sudo().create({'name': tag})
                    tmp_tags.append((4, lp_s[0].id))
        return tmp_tags
    def get_task(self,work_item):
        tmp_description = ''
        tmp_TeamProject = ''
        tmp_Changedate = ''
        tmp_area = ''
        tmp_IterationPath = ''
        tmp_CreatedDate = ''
        tmp_OriginalEstimate = ''
        tmp_RemainingWork = ''
        tmp_CompletedWork = ''
        tmp_assigned_to = ''
        tmp_finish_date = ''
        tmp_priority = ''
        tmp_Requirement = ''
        tmp_state = ''
        tmp_state_changedate = ''
        tags = ''
        tmp_task= {}
        if "Microsoft.VSTS.Common.StateChangeDate" in work_item.fields:
            tmp_state_changedate = datetime.strptime(work_item.fields["Microsoft.VSTS.Common.StateChangeDate"],"%Y-%m-%dT%H:%M:%S.%fz")  # use striptime because there was a difference between time (odoo,devops)
        else:
            tmp_state_changedate = False
        if "Microsoft.VSTS.CMMI.RequirementType" in work_item.fields:
            tmp_Requirement = work_item.fields["Microsoft.VSTS.CMMI.RequirementType"]
        if "System.Description" in work_item.fields:
            tmp_description = work_item.fields["System.Description"]
        if "System.TeamProject" in work_item.fields:
            tmp_TeamProject = work_item.fields["System.TeamProject"]
        if "System.ChangedDate" in work_item.fields:
            tmp_Changedate = datetime.strptime(work_item.fields["System.ChangedDate"],"%Y-%m-%dT%H:%M:%S.%fz")  # use striptime cause there was a difference between time (odoo,devops)
        else:
            tmp_Changedate=False
        if "System.AreaPath" in work_item.fields:
            tmp_area = work_item.fields["System.AreaPath"]
        if "System.IterationPath" in work_item.fields:
            tmp_IterationPath = work_item.fields["System.IterationPath"]
        if "System.CreatedDate" in work_item.fields:
            tmp_CreatedDate = work_item.fields["System.CreatedDate"]
        if "Microsoft.VSTS.Common.ClosedDate" in work_item.fields:
            tmp_finish_date = work_item.fields["Microsoft.VSTS.Common.ClosedDate"]
        else:
            tmp_finish_date = False
        if "Microsoft.VSTS.Scheduling.OriginalEstimate" in work_item.fields:
            tmp_OriginalEstimate = work_item.fields["Microsoft.VSTS.Scheduling.OriginalEstimate"]
        if "Microsoft.VSTS.Scheduling.RemainingWork" in work_item.fields:
            tmp_RemainingWork = work_item.fields["Microsoft.VSTS.Scheduling.RemainingWork"]
        if "Microsoft.VSTS.Scheduling.CompletedWork" in work_item.fields:
            tmp_CompletedWork = work_item.fields["Microsoft.VSTS.Scheduling.CompletedWork"]
        if "System.AssignedTo" in work_item.fields:
            tmp_assigned_to = self.search_user(work_item.fields["System.AssignedTo"])
        if "Microsoft.VSTS.Common.Priority" in work_item.fields:
            tmp_priority = work_item.fields["Microsoft.VSTS.Common.Priority"]
        else:
            tmp_priority = False
        if "System.State" in work_item.fields:
            state = work_item.fields["System.State"]
            if state == 'Done':
                tmp_state = 'done'
            elif state == 'Active':
                tmp_state = 'active'
            elif state == 'To Do':
                tmp_state = 'to_do'
            elif state == 'Closed':
                tmp_state = 'closed'
            elif state == 'Resolved':
                tmp_state = 'resolved'
            else:
                tmp_state = ''
        tmp_task = {
            'name': work_item.fields["System.Title"],
            'description': tmp_description,
            'lp_devops_completed_work': tmp_CompletedWork,
            'project_id': self.id,
            'lp_devops_project_name': tmp_TeamProject,
            'lp_devops_changed_date': tmp_Changedate,
            'lp_devops_area': tmp_area,
            'lp_devops_iteration': tmp_IterationPath,
            'lp_devops_start_date': tmp_CreatedDate,
            'lp_devops_original_estimate': tmp_OriginalEstimate,
            'lp_devops_remaining_work': tmp_RemainingWork,
            'lp_devops_finish_date': tmp_finish_date,
            'user_id': tmp_assigned_to,
            'lp_devops_priority': tmp_priority,
            'date_last_stage_update': tmp_state_changedate,
            'lp_task_state': tmp_state,
            'lp_devops_requirement': tmp_Requirement,
            'lp_devops_ref_id': work_item.id
        }
        return tmp_task

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
        count_insert = 0
        count_updates=0
        count_error_task = 0
        if wiql_results:
            tasks_to_be_synced = []
            odoo_task_ids = self.env['project.task'].search([('project_id', '=', self.id)]).ids

            for task in self.env['project.task'].browse(odoo_task_ids):
                try:
                 if task.lp_devops_ref_id: #odoo task already connected to devops task
                    work_item = wit_client.get_work_item(int(task.lp_devops_ref_id))
                    count_updates = count_updates + self.update_task(work_item,task)
                    tasks_to_be_synced.append(task.lp_devops_ref_id)
                except Exception as e:
                       count_error_task = count_error_task + 1
                       _logger.exception(e)


            tasks_to_be_inserted= [wit_client.get_work_item(int(tmp_devops_task.id)) for tmp_devops_task in wiql_results if tmp_devops_task.id not in tasks_to_be_synced]
            for work_item in tasks_to_be_inserted:
                 try:
                  count_insert = count_insert + self.insert_task(work_item)
                 except Exception as e:
                     count_error_task = count_error_task + 1
                     _logger.exception(e)

            return {
            'name': 'Information',
            'type': 'ir.actions.act_window',
            'res_model': 'project.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'context':{'default_lp_updates_counter':count_updates , 'default_lp_insert_counter':count_insert,'default_lp_error_counter':count_error_task},
            'target': 'new'
                }
    def get_email(self, AssignedTo=''):
        email = ''
        try:
            AssignedTo = str(AssignedTo).split()
            email = AssignedTo[-1]
        except :
            _logger.error('ERROR: email not valid on this task!')
        return email.strip("<>")

    def search_user(self,AssignedTo=''):
        email = self.get_email(AssignedTo)
        users = self.env['res.users'].sudo().search([('login', '=', email)])
        if users:
            return users[0].id
        else:
                return self.user_id.id

class LP_Popup_Wizard(models.TransientModel):
    _name = 'project.wizard'
    _description = 'Pop up Wizard'
    lp_updates_counter = fields.Integer('Updated tasks:', readonly=True)
    lp_insert_counter = fields.Integer('Inserted tasks:', readonly=True)
    lp_error_counter = fields.Integer('Error tasks:', readonly=True)



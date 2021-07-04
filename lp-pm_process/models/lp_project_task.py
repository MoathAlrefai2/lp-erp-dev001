# -*- coding: utf-8 -*-
from odoo import models, fields, api


class LP_Project_Task(models.Model):
    _inherit = ['project.task']

    lp_devops_priority = fields.Integer(string='Task Priority', readonly=True)
    #DevOps fields
    lp_devops_ref_id = fields.Integer('Reference Id', readonly=True)
    lp_devops_changed_date = fields.Datetime('Changed Date', readonly=True)
    lp_devops_project_name = fields.Char('Project Name', readonly=True)
    lp_devops_area = fields.Char('Area', readonly=True)
    lp_devops_iteration = fields.Char('Iteration', readonly=True)

    #Effort Hours
    lp_devops_original_estimate = fields.Char('Original Estimate', readonly=True)
    lp_devops_remaining_work = fields.Char('Remaining work', readonly=True)
    lp_devops_completed_work = fields.Char('Completed work', readonly=True)

    #Schedual
    lp_devops_start_date = fields.Date('Start Date', readonly=True)
    lp_devops_finish_date = fields.Date('Finish Date', readonly=True)

    #Tree Parents
    lp_devops_epic = fields.Char('Epic', readonly=True)
    lp_devops_feature = fields.Char('Feature', readonly=True)
    lp_devops_requirement = fields.Char('Requirement', readonly=True)

    lp_selection_tasks = [('to_do', 'To Do'), ('active', 'Active'), ('done', 'Done'), ('closed', 'Closed'),('resolved', 'Resolved')]
    lp_task_state = fields.Selection(lp_selection_tasks, string='State', readonly=True)

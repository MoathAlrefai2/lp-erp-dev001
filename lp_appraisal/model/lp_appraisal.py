from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError

class LP_Appraisal(models.Model):
    _inherit = 'hr.appraisal'

    lp_date_from = fields.Date(string='Date From')
    lp_date_to = fields.Date(string='Date To')
    lp_salary = fields.Float(string='Salary')
    lp_effective_date = fields.Date(string='Effective Date')
    lp_salary_raise = fields.Float(string='Salary Raise')
    lp_extra_points = fields.Float(string='Extra Points')
    lp_score_perc = fields.Float(string='Score Percantage',compute ='_compute_score_perc')
    lp_total_score = fields.Float(string='Total Score',compute ='_compute_total_score')#
    lp_job_id = fields.Many2one('hr.job', string='Current Job Position')
    lp_next_job_id = fields.Many2one('hr.job', string='Next Job Position')
    lp_total_salary = fields.Float(string='Total Salary',compute ='_compute_total_salary')#
    lp_next_review = fields.Date(string='Next Review Date')
    lp_performance_level = fields.Selection([('far_exceed', 'Far Exceed'),
                                          ('exceed', 'Exceed'),
                                          ('accomplish', 'Accomplish'),
                                          ('poor', 'Poor'),
                                          ('under_perf', 'Under Performance')],
                                         string='Performance Level')
    survey_ids = fields.One2many('employee.survey', 'appraisal_id', string='Employee Survey')
    answer_ids = fields.One2many('survey.user_input', 'appraisal_id', string='Answers')

    @api.depends('lp_score_perc')
    def _compute_score_perc(self):
        tot_in_months = 0.0
        total_num_of_month = 0.0
        if self.answer_ids:
            for answer in self.answer_ids:
                question_result = 0.0
                max_total = 0.0
                for input in answer.user_input_line_ids:
                    list_marks = []
                    for label in input.question_id.labels_ids:
                        list_marks.append(label.quizz_mark)
                    max_num = max(list_marks) if list_marks else 0
                    max_total += max_num
                    question_result += input.quizz_mark
                if max_total > 0.0:
                    tot_question_result = question_result / max_total
                    num_of_month = self.env['employee.survey'].search([('response_id', '=', answer.id)]).num_of_month
                    tot_in_months += tot_question_result * num_of_month
                    total_num_of_month += num_of_month
                    self.lp_score_perc = tot_in_months / total_num_of_month if total_num_of_month > 0.0 else 1

        else:
            if len(self.survey_ids) == 1:
                self.lp_score_perc = self.survey_ids.score_percentage

            else:
                total = 0.0
                total_month = 0
                for answer in self.survey_ids:
                    total_month += answer.num_of_month
                for rec in self.survey_ids:
                    total += rec.score_percentage * (rec.num_of_month / total_month)
                self.lp_score_perc = total




    @api.depends('lp_total_salary')
    def _compute_total_salary(self):
            self.lp_total_salary = self.lp_salary + self.lp_salary_raise

    @api.depends('lp_total_score')
    def _compute_total_score(self):
            self.lp_total_score = self.lp_score_perc + self.lp_extra_points



    @api.onchange('employee_id')
    def get_salary_job_position_create(self):
        if not self.id.origin and self.employee_id.id:
            last_employee_record = self.env['hr.appraisal'].search([('employee_id', '=', self.employee_id.id)], limit=1,order='create_date desc')
            self.lp_salary = last_employee_record[0].lp_salary
            self.lp_job_id =last_employee_record[0].lp_next_job_id



class LP_Hrjob(models.Model):
    _inherit = 'hr.job'
    surveys_ids = fields.Many2many('survey.survey', 'survey_id', string='Review Survey')

class EmployeeSurvey(models.Model):
    _name = 'employee.survey'
    _description='employee_survey'

    appraisal_id = fields.Many2one('hr.appraisal', string='Appraisal')
    employee_manager_id = fields.Many2one('hr.employee', string='Manager')
    response_id = fields.Many2one('survey.user_input', "Response")
    survey_id = fields.Many2one('survey.survey', string="Survey")
    status = fields.Selection([('draft', 'Draft'), ('done', 'Done')], string='Status', default='draft')
    num_of_month = fields.Integer(string='No. Of Month')
    from_date = fields.Date(string='From Date')
    to_date = fields.Date(string='To Date')
    score_percentage = fields.Float(string='Score Percantage')
    performance_levels = fields.Selection([('far_exceed', 'Far Exceed'),
                                          ('exceed', 'Exceed'),
                                          ('accomplish', 'Accomplish'),
                                          ('poor', 'Poor'),
                                          ('under_perf', 'Under Performance')], string='Performance Level',compute='_compute_perf_level')


    @api.depends('score_percentage')
    def _compute_perf_level(self):
            for rec in self:
              if rec.score_percentage > 0.0010 and rec.score_percentage <= 0.1240 :
               rec.performance_levels = 'poor'
              else:
               rec.performance_levels = False
              if rec.score_percentage >0.12410 and rec.score_percentage <=0.37500 :
               rec.performance_levels = 'under_perf'
              if rec.score_percentage >0.37510 and rec.score_percentage <=0.62500 :
               rec.performance_levels = 'accomplish'
              if rec.score_percentage >0.62510 and rec.score_percentage <=0.87500 :
               rec.performance_levels = 'exceed'
              if rec.score_percentage > 0.87510 and rec.score_percentage <= 1.00000:
                rec.performance_levels = 'far_exceed'
              if rec.score_percentage > 1.00000:
                  raise UserError('Score Percentage Must be less or equal than 1.0!')




class LP_Appraisalid(models.Model):
    _inherit = 'survey.user_input'
    appraisal_id = fields.Many2one('hr.appraisal', string='Appraisal')


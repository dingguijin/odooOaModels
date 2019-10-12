# -*- coding: utf-8 -*-
###################################################################################
# Copyright (C) 2019 SuXueFeng
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
###################################################################################
import datetime
import logging
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class LeaveApplication(models.Model):
    _name = 'oa.travel.application'
    _inherit = ['oa.base.model']
    _description = "出差申请"

    emp_id = fields.Many2one(comodel_name='hr.employee', string=u'申请人', required=True)
    sum_days = fields.Integer(string=u'总天数', compute='_compute_sum_days')
    line_ids = fields.One2many(comodel_name='oa.travel.application.line', inverse_name='oa_ta_id', string=u'明细')

    @api.model
    def create(self, values):
        values['form_number'] = self.env['ir.sequence'].sudo().next_by_code('oa.travel.application.code')
        return super(LeaveApplication, self).create(values)

    @api.depends('line_ids')
    def _compute_sum_days(self):
        for res in self:
            t_day = 0
            for line in res.line_ids:
                t_day += int(line.ta_days)
            res.sum_days = t_day


class LeaveApplicationLine(models.Model):
    _name = 'oa.travel.application.line'
    _description = u"出差申请列表"

    TATOOL = [
        ('飞机', '飞机'),
        ('火车', '火车'),
        ('汽车', '汽车'),
        ('船舶', '船舶'),
        ('其他', '其他'),
    ]

    sequence = fields.Integer(string=u'序号')
    start_date = fields.Date(string=u'开始日期')
    end_date = fields.Date(string=u'结束日期')
    departure_city = fields.Char(string='出发城市')
    destination_city = fields.Char(string='目的城市')
    ta_text = fields.Char(string=u'出差事由', help="请填写出差事由")
    ta_tool = fields.Selection(string=u'交通工具', selection=TATOOL, default='飞机')
    ta_type = fields.Selection(string=u'单程往返', selection=[('单程', '单程'), ('往返', '往返'), ], default='单程')
    ta_days = fields.Char(string=u'时长（天）')
    remarks = fields.Text(string=u'备注')
    oa_ta_id = fields.Many2one(comodel_name='oa.travel.application', string=u'出差申请', ondelete='cascade')

    @api.onchange('start_date', 'end_date')
    def onchange_date(self):
        if self.start_date and self.end_date:
            start_date = datetime.datetime.strptime(str(self.start_date), "%Y-%m-%d")
            end_date = datetime.datetime.strptime(str(self.end_date), "%Y-%m-%d")
            self.ta_days = str((end_date - start_date).days)


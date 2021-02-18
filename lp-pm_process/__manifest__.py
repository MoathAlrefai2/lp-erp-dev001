# -*- coding: utf-8 -*-
{
    'name': "lp-pm_process",

    'summary': """
        Modifications for PM process in Leading Point, https://leading-point.com/""",

    'description': """
        Modifications for PM process in Leading Point
    """,

    'author': "Leading Point",
    'website': "https://leading-point.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'PM',
    'version': '14.0.1',

    # any module necessary for this one to work correctly
    'depends': ['project'],
    'data': [
        'views/lp_project.xml',
    ],
}

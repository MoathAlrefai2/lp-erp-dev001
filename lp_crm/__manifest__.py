{
    'name':"lp_crm",
    "description":'(lp_crm) inherit from (crm.lead)',
    'summary': """
      Modifications for contact module , https://leading-point.com/""",
    'description': """
      Modifications for CRM
  """,

    'author': "Leading Point",
    'website': "https://leading-point.com",
    'data': [
        'security/lp_groups.xml',
        'security/ir.model.access.csv',
        'data/stages_data.xml',
        'data/automated_action.xml',
'data/lp_category.xml',
'views/lp_crm.xml'
    ],
    'version': '14.0.1',
     'category': 'Leading Point',
    'depends': ['base','crm','contacts','mail','base_automation']
}

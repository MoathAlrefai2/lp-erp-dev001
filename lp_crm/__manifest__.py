{
    'name':"lp_crm",
    "description":'(lp_crm) inherit from (crm.lead)',
    'summary': """
      Modifications for contact module , https://leading-point.com/""",

    'description': """
      Modifications for contact
  """,

    'author': "Leading Point",
    'website': "https://leading-point.com",
    'data': [
        'security/lp_groups.xml',
        'security/ir.model.access.csv',
'views/lp_crm.xml'
    ],
    # "data":[
    #     "views/lp_crm.xml"
    # ],
    'version': '14.0.1',
     'category': 'Tools',
    'depends': ['base','crm','contacts']
}

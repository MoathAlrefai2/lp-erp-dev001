{
    'name':"lp_appraisal",
    "description":'(lp_appraisal) inherit hr appraisal'  ,
    'summary': """Modifications for apprasial module , https://leading-point.com/""",

    'description': """
      Modifications for appraisal
  """,

    'author': "Leading Point",
    'website': "https://leading-point.com",
 'data': [
     'security/ir.model.access.csv',
'views/lp_appraisal.xml'
    ],
     'category': 'Leading Point',
    'depends':
        ['hr','survey','base','hr_appraisal']

}

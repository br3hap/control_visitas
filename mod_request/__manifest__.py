# -*- coding: utf-8 -*-
{
    'name': "mod_request",

    'summary': """
        Module Requirements and Request""",

    'description': """        
        The registry considers that the request can be of the Judicial or \n
        Administrative type, or if it is a purchase, transfer or \n
        reimbursement from a lawsuit. The type of request and the \n
        process will influence the flow of work.
    """,

    'author': "CONASTEC",
    'website': "https://www.conastec.com.pe/",
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mail','hr_expense','account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/sequence.xml',
        'views/mod_request.xml',
        'views/mod_request_action_tree.xml',
        'reports/report_mod_request.xml',
        'reports/template_mod_template.xml',
        'views/rest_api_token.xml',
        'views/mod_requirements.xml',
        'views/mod_request_masive_paid_view.xml',
        'wizard/mod_requirement_text.xml',
        'wizard/mod_request_check_list.xml',
        # 'views/res_users.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

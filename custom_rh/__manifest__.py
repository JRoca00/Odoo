{

    'name': 'Reportes Recursos Humanos',
    'version': '14.0.1.0.0',
    'category': 'Extra Tools',
    'summary': 'Reportes Recursos Humanos',
    'license': 'AGPL-3',
    'author': 'Panela Bits',
    'maintainer': 'Panela Bits',
    'website': 'https://panelabits.com',
    'depends': [
        'hr',
        'hr_holidays',
        ],
    'demo': [],
    'data': [
        'security/ir.model.access.csv',
        'report/hr_employee_report_ingresos.xml',
        'report/hr_employee_report_CLaboral.xml',
        'report/hr_employee_report_ACuenta.xml',
        'report/report_prestaciones.xml',
        'report/hr_employee.xml',
        'views/hr_employee.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}

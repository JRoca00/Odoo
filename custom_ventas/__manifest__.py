{

    'name': 'Ventas',
    'version': '15.0.1.0.0',
    'category': 'Extra Tools',
    'summary': 'Mostrar ventas con proveedor',
    'license': 'AGPL-3',
    'author': 'Panela Bits',
    'maintainer': 'Panela Bits',
    'website': 'https://panelabits.com',
    'depends': ['sale','contacts'],
    'demo': [],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order.xml',
        'report/recibo.xml',
        'report/appointment.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
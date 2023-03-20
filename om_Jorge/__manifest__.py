{

    'name': 'Prueba_Jorge',
    'version': '15.0.1.0.0',
    'category': 'Extra Tools',
    'summary': 'Modulo de prueba',
    'sequence': '10',
    'license': 'AGPL-3',
    'author': 'Jorge',
    'maintainer': 'Jorge',
    'website': 'odoomates.com',
    'depends': ['sale','account'],
    'demo': [],
    'data': [
        'security/ir.model.access.csv',
        'views/account.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
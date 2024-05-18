{
    "name": "Analytic Account - Stock Picking",
    "summary": "Costos de movimientos de inventario y Distribucion Analitica",
    "version": "16.0.1.0.0",
    "sequence": "1",
    "author": "Panela Bits, S.E. ",
    "website": "https://panelabits.com",
    "category": "Warehouse Management",
    "license": "AGPL-3",
    "depends": ["base","stock_account", "analytic", "project"],
    "data": [
        "views/stock_move_views.xml",
        "views/stock_move_line_views.xml",
        "views/stock_picking_views.xml",
        "views/project_project_views.xml",
    ],
    "installable": True,
    "application": True,
}

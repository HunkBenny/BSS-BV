{
    'name': 'Excel Odoo Connector',
    'version': '1.0.4',
    'summary': '''
    Data connection and synchronization,
    Excel Connector for Odoo Data,
    Odoo Excel Connector LibreOffice,
    Odoo Excel Data Connector,
    LibreOffice Connector excel to database,
    Excel Connect to Odoo,
    Excel Office Document Connection to Odoo,
    LibreOffice Connect excel to Odoo Data,
    Generate ODC Odoo, 
    Excel Data Connection Template, 
    Auto synchronization data,
    LibreOffice Sync data to excel,
    ERP Excel Data Connection LibreOffice,
    Office Document Connection for Odoo,
    Export Odoo Data Excel,
    Excel Report Connector,
    Project Tasks to Excel,
    Accounting Report to Excel,
    Connect Account Report to Excel,
    LibreOffice Calc Link External Data from Odoo,
    OpenOffice Link External Data from Odoo,
    All In One Excel Report,
    All In One Report,
    Quotations Excel Report,
    Sale Order Excel Report,
    Sales Order Excel Report,
    Request For Quotation Excel Report,
    RFQ Excel Report,
    Supplier Invoice Excel Report,
    Customer Invoice Excel Report,
    Invoice Excel Report,
    Invoice Report,
    Invoices Excel Report,
    Delivery Order Excel Report,
    Delivery Order Report,
    XLS Report,
    XLSX Report,
    ''',
    'category': 'Extra Tools,Accounting,Purchases,Sales,Project,Productivity',
    'author': 'XFanis',
    'support': 'odoo@xfanis.dev',
    'website': 'https://xfanis.dev/odoo.html',
    'live_test_url': 'https://youtu.be/HLWMkJTb-IQ',
    'license': 'OPL-1',
    'price': 35,
    'currency': 'EUR',
    'description':
        """
Excel Odoo Connector
====================
Data connection and synchronization

-----------------------------------
        """,
    'depends': ['web'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/odc_template.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'xf_excel_odoo_connector/static/src/js/odc_template_list_controller.js',
        ],
        'web.assets_qweb': [
            'xf_excel_odoo_connector/static/src/xml/odc_template_button.xml',
        ],
    },
    'images': [
        'static/description/xf_excel_odoo_connector.png',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
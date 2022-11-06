# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name": "Purchases Excel Reports | Purchases Order Excel Reports | Request For Quotation Excel Reports | Purchase Excel Report | Purchase Orders Excel Report ",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "version": "15.0.2",
    "license": "OPL-1",
    "category": "Purchases",
    "summary": "Merge Excel Report Of Purchase Order, Combine Purchase Order Excel Report, Mass Excel Report, Bulk Purchase Excel Report,RFQ Excel Report,Print Purchase Excel Report,Print Purchase Order Excel Report,Download Purchase Excel Report Odoo", 
    "description":  """If you want to get excel reports of purchase order/request for quotation. So here we build a module that can help to print the excel report of the purchase order/request for quotation. You can get an excel report separate sheet of each order also. Cheers!""",
    "depends": [
        'purchase','purchase_requisition',
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/purchase_order_inherit_view.xml",
        "views/purchase_report_xlsx_view.xml",
        "views/purchase_quotation_inherit_view.xml",
        "views/purchase_quotation_xlsx_view.xml",
        "report/call_for_tenders_xls_report_wizard.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
    "images": ["static/description/background.png"],
    "price": "15",
    "currency": "EUR"
}

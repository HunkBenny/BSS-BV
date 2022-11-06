# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import fields, models
import xlwt
import base64
from io import BytesIO


class PurchaseRequisitionDetailExcelExtended(models.Model):
    _name = "purchase.requisition.detail.excel.extended"
    _description = 'Excel Call for Tenders Extended'

    excel_file = fields.Binary('Download report Excel')
    file_name = fields.Char('Excel File', size=64)

    def download_report(self):

        return{
            'type': 'ir.actions.act_url',
            'url': 'web/content/?model=purchase.requisition.detail.excel.extended&field=excel_file&download=true&id=%s&filename=%s' % (self.id, self.file_name),
            'target': 'new',
        }


class PurchaseRequisition(models.Model):
    _inherit = "purchase.requisition"

    def action_requisition_xls_entry(self):
        action = self.env['ir.actions.act_window']._for_xml_id(
            'sh_purchase_excel.sh_requisition_details_report_wizard_form_action')
        # Force the values of the move line in the context to avoid issues
        ctx = dict(self.env.context)
        ctx.pop('active_id', None)
        ctx['active_ids'] = self.ids
        ctx['active_model'] = 'purchase.requisition'
        action['context'] = ctx
        return action


class ShPurchaseRequisitionDetailsReportWizard(models.TransientModel):
    _name = "sh.purchase.requisition.details.report.wizard"
    _description = 'Call for Tenders details report wizard model'

    def print_journal_entries_xls_report(self):
        workbook = xlwt.Workbook()
        heading_format = xlwt.easyxf(
            'font:height 310,bold True;pattern: pattern solid, fore_colour gray25;align: horiz left, vertical center;borders:top thick;borders:bottom thick;')
        bold = xlwt.easyxf(
            'font:bold True;pattern: pattern solid, fore_colour gray25;align: horiz left')
        format1 = xlwt.easyxf('font:bold True;;align: horiz left')

        data = {}
        data = dict(data or {})
        active_ids = self.env.context.get('active_ids')

        Requisition = self.env['purchase.requisition'].search(
            [('id', 'in', active_ids)])

        NO = 0
        for record in Requisition:
            NO += 1
            product_lines = []
            purchase_lines = []
            final_value = {}

            final_value['name'] = record.name
            final_value['ordering_date'] = record.ordering_date
            final_value['type_id'] = record.type_id.name
            final_value['origin'] = record.origin

            for lines in record.line_ids:
                product = {
                    'code': lines.product_id.code,
                    'product_id': lines.product_id.name,
                    'product_qty': lines.product_qty,
                    'category_id': lines.product_uom_id.category_id.name,
                    'schedule_date': lines.schedule_date,
                }
                product_lines.append(product)

            for lines in record.purchase_ids:
                purchase = {
                    'partner_id': lines.partner_id.name,
                    'date_order': lines.date_order,
                    'name': lines.name,
                }
                purchase_lines.append(purchase)

            if record.name == 'New':
                Name = 'New ' + str(NO)
                worksheet = workbook.add_sheet(
                    str(Name), cell_overwrite_ok=True)
            else:
                worksheet = workbook.add_sheet(
                    record.name, cell_overwrite_ok=True)
            heading = 'Call for Tenders ' + str(final_value['name'])
            worksheet.write_merge(
                0, 2, 0, 3, heading, heading_format)

            worksheet.col(0).width = int(30 * 260)
            worksheet.col(1).width = int(30 * 260)
            worksheet.col(2).width = int(30 * 260)
            worksheet.col(3).width = int(30 * 260)

            worksheet.write(4, 0, "Call for Tender Reference : ", format1)
            worksheet.write(4, 1, "Scheduled Ordering Date : ", format1)
            worksheet.write(4, 2, "Selection Type : ", format1)
            worksheet.write(4, 3, "Source : ", format1)

            worksheet.write(5, 0, final_value['name'])
            if final_value['ordering_date']:
                worksheet.write(5, 1, str(final_value['ordering_date']))
            else:
                worksheet.write(5, 1, '')
            worksheet.write(5, 2, final_value['type_id'])
            if final_value['origin']:
                worksheet.write(5, 3, str(final_value['origin']))
            else:
                worksheet.write(5, 3, '')

            row = 7

            if record.line_ids:
                worksheet.write_merge(
                    row, row+1, 0, 3, "Products", heading_format)

                worksheet.write(row+3, 0, "Description", bold)
                worksheet.write(row+3, 1, "Qty", bold)
                worksheet.write(row+3, 2, "Product UoM", bold)
                worksheet.write(row+3, 3, "Scheduled Date", bold)
                row = row+4
                for rec in product_lines:
                    if rec.get('code') and rec.get('product_id'):
                        name = '[' + str(rec.get('code')) + ']' + \
                            str(rec.get('product_id'))
                        worksheet.write(row, 0, name)
                    if rec.get('product_qty'):
                        worksheet.write(row, 1, str(rec.get('product_qty')))
                    if rec.get('category_id'):
                        worksheet.write(row, 2, rec.get('category_id'))
                    if rec.get('schedule_date'):
                        worksheet.write(row, 3, str(rec.get('schedule_date')))

                    row += 1

            if record.purchase_ids:
                row += 1
                worksheet.write_merge(
                    row, row+1, 0, 3, "Requests for Quotation Details", heading_format)

                worksheet.write(row+3, 0, "Vendor", bold)
                worksheet.write(row+3, 1, "Date", bold)
                worksheet.write(row+3, 2, "Reference", bold)

                row = row+4
                for rec in purchase_lines:
                    if rec.get('partner_id'):
                        worksheet.write(row, 0, rec.get('partner_id'))
                    if rec.get('date_order'):
                        worksheet.write(row, 1, str(rec.get('date_order')))
                    if rec.get('name'):
                        worksheet.write(row, 2, rec.get('name'))

                    row += 1

        filename = ('Call for Tenders Detail Xls Report' + '.xls')
        fp = BytesIO()
        workbook.save(fp)
        export_id = self.env['purchase.requisition.detail.excel.extended'].sudo().create({
            'excel_file': base64.encodebytes(fp.getvalue()),
            'file_name': filename,
        })

        return{
            'type': 'ir.actions.act_url',
            'url': 'web/content/?model=purchase.requisition.detail.excel.extended&field=excel_file&download=true&id=%s&filename=%s' % (export_id.id, export_id.file_name),
            'target': 'new',
        }

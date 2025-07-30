# Copyright 2022 - Komun.org Álex Berbel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
import binascii
import tempfile
import xlrd
from tempfile import TemporaryFile
from odoo.exceptions import UserError, ValidationError
import logging
import io
import filetype
import pandas as pd
import base64
import csv

_logger = logging.getLogger(__name__)
		
class order_line_wizard(models.TransientModel):

	_name='order.line.wizard'
	_description = "Order Line Wizard"

	sale_order_file = fields.Binary(string="Select File", help="Ficheros aceptados: .xls, .xlsx")
	clean_order_lines = fields.Boolean(string="Limpiar lineas de pedido", help="Si seleccionas esta opción se borrarán "
																			   "todas las líneas de pedido actuales y "
																			   "se reemplazarán por las que se incluyan "
																			   "en el fichero seleccionado.")

	def import_sol(self):
		file = base64.b64decode(self.sale_order_file)
		extension = self.get_file_extension(file)

		if extension == 'csv':
			values = self.parse_csv_file(file)
		elif extension == 'xlsx':
			values = self.parse_xlsx_file(file)
		else:
			raise UserError(_('Wrong file type.'))

		active_sale_order = self.env['sale.order'].browse(self._context.get('active_id'))
		if active_sale_order.state in ['draft', 'sent']:
			if self.clean_order_lines:
				for line in active_sale_order.order_line:
					line.unlink()

			for value in values:
				self.create_order_line(value, active_sale_order)
		else:
			raise UserError(_('We cannot import data in validated or confirmed order.'))

	def get_file_extension(self, file):
		kind = filetype.guess(file)

		if kind is None:
			_logger.warning("Cannot guess file type!")
			return

		_logger.debug(f"File MIME type: {kind.mime}")
		_logger.debug(f"File extension: {kind.extension}")

		return kind.extension

	def parse_xlsx_file(self, file):
		xls = pd.ExcelFile(file)
		df = xls.parse(xls.sheet_names[0])
		df = df.fillna('')
		return df.values.tolist()

	def parse_csv_file(self, file):
		pass # ToDo

	def create_order_line(self, values, sale_order):
		product = self.get_product(values[0])

		self.env['sale.order.line'].create({
			'order_id': sale_order.id,
			'product_id': product.id,
			'product_uom_qty': values[1],
			'name': values[2],
			'price_unit': values[3],
			'tax_id': self.get_tax_ids(values[4], product),
			'discount': values[5]
		})

	def get_product(self, product_code):

		search_fields = [
			# (model, field) - In search order
			('product.product', 'barcode'),
			('product.template', 'isbn_number'),
			('product.product', 'name'),
			('product.product', 'default_code')
		]

		product = None
		for model, field in search_fields:
			product = self.env[model].search([(field, '=', product_code)], limit=1)
			if product:
				break

		if not product:
			raise ValidationError(_('%s product is not found.') % product_code)

		return product

	def get_tax_ids(self, taxes, product):
		tax_id_lst=[]
		if taxes:
			if type(taxes) is float:
				taxes = str(int(taxes))
			tax_names = taxes.split(';')
			if len(tax_names) == 1:
				tax_names = taxes.split(',')

			for name in tax_names:
				if "% G" not in name:
					if "%" in name:
						name += " G"
					else:
						name += "% G"
				_logger.debug("TAX: " + name)
				tax = self.env['account.tax'].search([('name', '=', name), ('type_tax_use', '=', 'sale')])
				if not tax:
					raise ValidationError(_('"%s" Tax not in your system') % name)
				tax_id_lst.append(tax.id)
		else:
			# Get default from product
			for tax in product.mapped('taxes_id').ids:
				tax_id_lst.append(tax)

		return tax_id_lst

	def download_sample_file(self):
		return {
             'type' : 'ir.actions.act_url',
             'url': '/web/binary/download_demo_importar_ventas',
             'target': 'new',
		 }
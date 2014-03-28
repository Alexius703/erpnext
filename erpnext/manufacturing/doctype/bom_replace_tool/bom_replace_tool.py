# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cstr, flt
from frappe.model.code import get_obj
from frappe import msgprint, _
	
from frappe.model.document import Document

class BomReplaceTool(Document):
	def replace_bom(self):
		self.validate_bom()
		self.update_new_bom()
		bom_list = self.get_parent_boms()
		updated_bom = []
		for bom in bom_list:
			bom_obj = get_obj("BOM", bom, with_children=1)
			updated_bom = bom_obj.update_cost_and_exploded_items(updated_bom)
			
		frappe.msgprint(_("BOM replaced"))

	def validate_bom(self):
		if cstr(self.current_bom) == cstr(self.new_bom):
			msgprint("Current BOM and New BOM can not be same", raise_exception=1)
	
	def update_new_bom(self):
		current_bom_unitcost = frappe.db.sql("""select total_cost/quantity 
			from `tabBOM` where name = %s""", self.current_bom)
		current_bom_unitcost = current_bom_unitcost and flt(current_bom_unitcost[0][0]) or 0
		frappe.db.sql("""update `tabBOM Item` set bom_no=%s, 
			rate=%s, amount=qty*%s where bom_no = %s and docstatus < 2""", 
			(self.new_bom, current_bom_unitcost, current_bom_unitcost, self.current_bom))
				
	def get_parent_boms(self):
		return [d[0] for d in frappe.db.sql("""select distinct parent 
			from `tabBOM Item` where ifnull(bom_no, '') = %s and docstatus < 2""",
			self.new_bom)]
# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2019-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Milind Mohan @ Cybrosys, (odoo@cybrosys.com)
#            Mohammed Shahil M P @ Cybrosys, (odoo@cybrosys.com)
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
from odoo import models, fields, api, _


class ProductProduct(models.Model):
    _inherit = 'product.template'

    is_a_parts = fields.Boolean(
        'Is a Mobile Part', default=False,
        help="Specify if the product is a mobile part or not.")

    brand_name = fields.Many2one('mobile.brand', string="Brand", help="Select a mobile brand for the part")
    model_name = fields.Many2one('brand.model', string="Model Name", domain="[('mobile_brand_name','=',brand_name)]",
                                 help="Select a model for the part")
    model_colour = fields.Char(string="Colour", help="colour for the part")
    extra_descriptions = fields.Text(string="Note")
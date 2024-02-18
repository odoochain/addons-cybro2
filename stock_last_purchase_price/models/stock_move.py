# -*- coding: utf-8 -*-
################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Sruthi Renjith (odoo@cybrosys.com)
#
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
################################################################################
from collections import defaultdict
from odoo import models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero


class StockMove(models.Model):
    """ Class to inherit stock_move to update the product price """
    _inherit = "stock.move"

    def product_price_update_before_done(self, forced_qty=None):
        """ Function to update the price of the product """
        tmpl_dict = defaultdict(lambda: 0.0)
        # Adapt standard price on incoming moves if the product cost_method
        # is 'average'
        std_price_update = {}
        for move in self.filtered(lambda move: move.location_id.usage in (
                'supplier', 'production') and move.product_id.cost_method in (
                                                       'average', 'last')):
            product_tot_qty_available = move.product_id.qty_available + \
                                        tmpl_dict[move.product_id.id]
            rounding = move.product_id.uom_id.rounding
            qty_done = 0.0
            if float_is_zero(product_tot_qty_available,
                             precision_rounding=rounding):
                new_std_price = move._get_price_unit()
            elif float_is_zero(product_tot_qty_available + move.product_qty,
                               precision_rounding=rounding) or \
                    float_is_zero(product_tot_qty_available + qty_done,
                                  precision_rounding=rounding):
                new_std_price = move._get_price_unit()
            else:
                # Get the standard price
                if move.product_id.cost_method == 'average':
                    amount_unit = std_price_update.get(
                        (move.company_id.id,
                         move.product_id.id)) or move.product_id.standard_price
                    qty_done = move.product_uom._compute_quantity(
                        move.quantity_done, move.product_id.uom_id)
                    qty = forced_qty or qty_done
                    new_std_price = ((amount_unit * product_tot_qty_available)
                                     + (move._get_price_unit() * qty)) / (
                                            product_tot_qty_available +
                                            qty_done)
            if (move.product_id.cost_method == 'last' and
                    move.product_id.valuation == 'real_time' or
                    move.product_id.valuation == 'manual_periodic'):
                new_std_price = move._get_price_unit()
                products = self.env['product.product'].browse(
                    move.product_id.id)
                account_id = (
                        products.property_account_creditor_price_difference.id
                        or products.categ_id.property_account_creditor_price_difference_categ.id)
                if not account_id:
                    raise UserError(
                        _('Configuration error. Please configure the price '
                          'difference account on the product or its category '
                          'to process this operation.'))
                products.create_price_change_account_move(new_std_price,
                                                          account_id,
                                                          move.company_id.id,
                                                          move.origin)
            tmpl_dict[move.product_id.id] += qty_done
            # Write the standard price, as SUPERUSER_ID because a warehouse
            # manager may not have the right to write on products
            move.product_id.with_context(
                force_company=move.company_id.id).sudo().write(
                {'standard_price': new_std_price})
            std_price_update[
                move.company_id.id, move.product_id.id] = new_std_price

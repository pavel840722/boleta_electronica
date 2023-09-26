from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError

class PartnerBoleta(models.Model):
    _inherit = 'res.partner'

    flag = fields.Boolean('Tipo Cliente')

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    service_order = fields.Char('Orden de Servicio')

# class SaleOrder(models.Model):
#     _inherit = 'sale.order'

    # def action_generar_boleta1(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    #     result = super(SaleOrder, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
    #                                                     submenu=submenu)
    #     if toolbar and self.env.user.partner_id.flag:
    #         for action in result['toolbar']['action']:
    #             if action['name'] == 'Generar Boletas':
    #                 result['toolbar']['action'].remove(action)
    #     return result

    # def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    #     result = super(SaleOrder, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
    #     if toolbar and self.partner_id.flag:
    #         for action in result['toolbar']['action']:
    #             if action['name'] == 'Generar Boletas':
    #                 result['toolbar']['action'].remove(action)
    #     return result



class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    service_order = fields.Char('Orden de Servicio')



class GenerarBoletas(models.Model):
    _inherit = 'sale.order'

    def action_generar_boletas(self):
        for venta in self:
            if venta.state != 'sale':
                raise ValidationError(_("La nota de venta no esta confirmada."))

            if venta.invoice_count == 0:
                if venta.partner_id.flag:
                    boleta = venta.env['account.move']

                    for obj in venta.order_line:
                        if obj.display_type == False:
                          invoice_line_ids = []
                          invoice_line_ids.append((0,0,{
                            'product_id':obj.product_id,
                            'name':obj.name,
                            'quantity':obj.product_uom_qty,
                            'price_unit':obj.price_unit,
                            'tax_ids':obj.tax_id,
                            'price_subtotal':obj.price_subtotal,

                          }))
                          partner_id = venta.env['res.partner'].search([('name','=','Consumidor Final Anónimo')]).id
                          boleta_id = boleta.create({
                            'partner_id': partner_id,
                            'invoice_line_ids':invoice_line_ids,
                            'move_type':'out_invoice',
                            'l10n_latam_document_type_id':5,
                            'ref': obj.service_order,
                            'invoice_origin': venta.name,
                          }).id
                          boleta_id = boleta.search([('id', '=', boleta_id)]).invoice_line_ids[0].id
                          venta.env.cr.execute('insert into sale_order_line_invoice_rel (invoice_line_id,order_line_id) values(%s,%s)', (boleta_id, obj.id))
                else:
                    raise ValidationError(_("El cliente de la venta no puede generar boletas."))
            else:
                raise ValidationError(_("La nota de venta ya tiene boletas generadas."))








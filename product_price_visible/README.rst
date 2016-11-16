Product Price Visible
=====================

This module comes from the community module "product_price_visible",
you can access by this link
https://github.com/Vauxoo/addons-vauxoo/tree/8.0/product_price_visible .
When installing this comminity module- 8.0, it can be installed without
errors. But the adjustments can not be applied. So there are some new
adjustment in this module to meet with customer's requirement -- assign
access rights of cost price to a specific group named "cost price visible".
You can check the following information to find the new adjustment.
1. The new group changed to "Cost Price Visible"
2. Change the model name to "product.template" instead of "product.product"
   in product_view.xml
3. Edit the "view_product_standard_price_inh_visible_form" in product_view.xml
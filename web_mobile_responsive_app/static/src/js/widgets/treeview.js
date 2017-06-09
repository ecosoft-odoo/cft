/*
 *    Copyright (c) 2015 - Present Ahmed Magdy
 *    All Rights Reserved
 *    Author: Ahmed Magdy <ahmed.magdy40@gmail.com>
 *
 *    This program is free software: you can redistribute it and/or modify
 *    it under the terms of the GNU General Public License as published by
 *    the Free Software Foundation, either version 3 of the License, or
 *    (at your option) any later version.
 *
 *    This program is distributed in the hope that it will be useful,
 *    but WITHOUT ANY WARRANTY; without even the implied warranty of
 *    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *    GNU General Public License for more details.
 *
 *    A copy of the GNU General Public License is available at:
 *    <http://www.gnu.org/licenses/gpl.html>.
 */

(function(){
    var instance = openerp;
    var QWeb = instance.web.qweb,
          _t =  instance.web._t,
          _lt = instance.web._lt;

    instance.web.TreeView.include(/** @lends instance.web.TreeView# */{
        load_tree: function (fields_view) {
            var self = this;
            var has_toolbar = !!fields_view.arch.attrs.toolbar;
            // field name in OpenERP is kinda stupid: this is the name of the field
            // holding the ids to the children of the current node, why call it
            // field_parent?
            this.children_field = fields_view['field_parent'];
            this.fields_view = fields_view;
            _(this.fields_view.arch.children).each(function (field) {
                if (field.attrs.modifiers) {
                    field.attrs.modifiers = JSON.parse(field.attrs.modifiers);
                }
            });
            this.fields = fields_view.fields;
            this.hook_row_click();
            this.$el.html(QWeb.render('ResponsiveTreeView', {
                'title': this.fields_view.arch.attrs.string,
                'fields_view': this.fields_view.arch.children,
                'fields': this.fields,
                'toolbar': has_toolbar
            }));
            this.$el.addClass(this.fields_view.arch.attrs['class']);

            this.dataset.read_slice(this.fields_list()).done(function(records) {
                if (!has_toolbar) {
                    // WARNING: will do a second read on the same ids, but only on
                    //          first load so not very important
                    self.getdata(null, _(records).pluck('id'));
                    return;
                }

                var $select = self.$el.find('select')
                    .change(function () {
                        var $option = $(this).find(':selected');
                        self.getdata($option.val(), $option.data('children'));
                    });
                _(records).each(function (record) {
                    self.records[record.id] = record;
                    $('<option>')
                            .val(record.id)
                            .text(record.name)
                            .data('children', record[self.children_field])
                        .appendTo($select);
                });

                if (!_.isEmpty(records)) {
                    $select.change();
                }
            });

            // TODO store open nodes in url ?...
            this.do_push_state({});

            if (!this.fields_view.arch.attrs.colors) {
                return;
            }
            this.colors = _(this.fields_view.arch.attrs.colors.split(';')).chain()
                .compact()
                .map(function(color_pair) {
                    var pair = color_pair.split(':'),
                        color = pair[0],
                        expr = pair[1];
                    return [color, py.parse(py.tokenize(expr)), expr];
                }).value();
        },
        
    });

})();
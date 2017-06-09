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

	
    instance.web.ListView.include( /** @lends instance.web.ListView# */ {
        _template: 'ResponsiveListView',
        load_list: function(data) {
        var self = this;
        this.fields_view = data;
        this.name = "" + this.fields_view.arch.attrs.string;

        if (this.fields_view.arch.attrs.colors) {
            this.colors = _(this.fields_view.arch.attrs.colors.split(';')).chain()
                .compact()
                .map(function(color_pair) {
                    var pair = color_pair.split(':'),
                        color = pair[0],
                        expr = pair[1];
                    return [color, py.parse(py.tokenize(expr)), expr];
                }).value();
        }

        if (this.fields_view.arch.attrs.fonts) {
            this.fonts = _(this.fields_view.arch.attrs.fonts.split(';')).chain().compact()
                .map(function(font_pair) {
                    var pair = font_pair.split(':'),
                        font = pair[0],
                        expr = pair[1];
                    return [font, py.parse(py.tokenize(expr)), expr];
                }).value();
        }

        this.setup_columns(this.fields_view.fields, this.grouped);

        this.$el.html(QWeb.render(this._template, this));
        this.$el.addClass(this.fields_view.arch.attrs['class']);

        // Head hook
        // Selecting records
        this.$el.find('.oe_list_record_selector').click(function(){
            self.$el.find('.oe_list_record_selector input').prop('checked',
                self.$el.find('.oe_list_record_selector').prop('checked')  || false);
            var selection = self.groups.get_selection();
            $(self.groups).trigger(
                'selected', [selection.ids, selection.records]);
        });

        // Add button
        if (!this.$buttons) {
            this.$buttons = $(QWeb.render("ListView.buttons", {'widget':self}));
            if (this.options.$buttons) {
                this.$buttons.appendTo(this.options.$buttons);
            } else {
                this.$el.find('.oe_list_buttons').replaceWith(this.$buttons);
            }
            this.$buttons.find('.oe_list_add')
                    .click(this.proxy('do_add_record'))
                    .prop('disabled', this.grouped);
        }

        // Pager
        if (!this.$pager) {
            this.$pager = $(QWeb.render("ResponsiveListView.pager", {'widget':self}));
            if (this.options.$buttons) {
                this.$pager.appendTo(this.options.$pager);
            } else {
                this.$el.find('.oe_list_pager').replaceWith(this.$pager);
            }

            this.$pager
                .on('click', 'a[data-pager-action]', function () {
                    var $this = $(this);
                    var max_page_index = Math.ceil(self.dataset.size() / self.limit()) - 1;
                    switch ($this.data('pager-action')) {
                        case 'first':
                            self.page = 0;
                            break;
                        case 'last':
                            self.page = max_page_index;
                            break;
                        case 'next':
                            self.page += 1;
                            break;
                        case 'previous':
                            self.page -= 1;
                            break;
                    }
                    if (self.page < 0) {
                        self.page = max_page_index;
                    } else if (self.page > max_page_index) {
                        self.page = 0;
                    }
                    self.reload_content();
                }).find('.oe_list_pager_state')
                    .click(function (e) {
                        e.stopPropagation();
                        var $this = $(this);

                        var $select = $('<select class="col-md-12 col-xs-12 col-sm-12 btn btn-default">')
                            .appendTo($this.empty())
                            .click(function (e) {e.stopPropagation();})
                            .append('<option value="80">80</option>' +
                                    '<option value="200">200</option>' +
                                    '<option value="500">500</option>' +
                                    '<option value="2000">2000</option>' +
                                    '<option value="NaN">' + _t("Unlimited") + '</option>')
                            .change(function () {
                                var val = parseInt($select.val(), 10);
                                self._limit = (isNaN(val) ? null : val);
                                self.page = 0;
                                self.reload_content();
                            }).blur(function() {
                                $(this).trigger('change');
                            })
                            .val(self._limit || 'NaN');
                    });
        }

        // Sidebar
        if (!this.sidebar && this.options.$sidebar) {
            this.sidebar = new instance.web.Sidebar(this);
            this.sidebar.appendTo(this.options.$sidebar);
            this.sidebar.add_items('other', _.compact([
                { label: _t("Export"), callback: this.on_sidebar_export },
                self.is_action_enabled('delete') && { label: _t('Delete'), callback: this.do_delete_selected }
            ]));
            this.sidebar.add_toolbar(this.fields_view.toolbar);
            this.sidebar.$el.hide();
        }
        //Sort
        var default_order = this.fields_view.arch.attrs.default_order,
            unsorted = !this.dataset._sort.length;
        if (unsorted && default_order && !this.grouped) {
            this.dataset.set_sort(default_order.split(','));
        }

        if(this.dataset._sort.length){
            if(this.dataset._sort[0].indexOf('-') == -1){
                this.$el.find('th[data-id=' + this.dataset._sort[0] + ']').addClass("sortdown");
            }else {
                this.$el.find('th[data-id=' + this.dataset._sort[0].split('-')[1] + ']').addClass("sortup");
            }
        }
        this.trigger('list_view_loaded', data, this.grouped);
        },
    });

})();
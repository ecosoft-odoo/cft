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


(function () {
    var instance = openerp;
    var QWeb = instance.web.qweb,
        _t = instance.web._t,
        _lt = instance.web._lt;



    instance.web.ListView.include({
        start_edition: function (record, options) {
            var self = this;
            this.edit_inline_cond = true;
            this.editor.edit_inline_cond = true;
            var item = false;
            if (record) {
                item = record.attributes;
                this.dataset.select_id(record.get('id'));
            } else {
                record = this.make_empty_record(false);
                this.records.add(record, {
                    at: this.prepends_on_create() ? 0 : null
                });
            }
            return this.ensure_saved().then(function () {
                return $.when.apply(null, self.editor.form.render_value_defs);
            }).then(function () {
                var $recordRow = self.groups.get_row_for(record);
                var cells = self.get_cells_for($recordRow);
                var fields = {};
                self.fields_for_resize.splice(0, self.fields_for_resize.length);
                return self.with_event('edit', {
                    record: record.attributes,
                    cancel: false
                }, function () {
                    return self.editor.edit(item, function (field_name, field) {
                        var cell = cells[field_name];
                        if (!cell) {
                            return;
                        }

                        // FIXME: need better way to get the field back from bubbling (delegated) DOM events somehow
                        field.$el.attr('data-fieldname', field_name);
                        fields[field_name] = field;
                        self.fields_for_resize.push({
                            field: field,
                            cell: cell
                        });
                    }, options).then(function () {
                        $recordRow.addClass('oe_edition');
                        if (self.edit_inline_cond) {
                            self.resize_fields();
                        } else {
                            self.show_edit_form($recordRow);
                        }
                        if (self.editor.form.inline_form_footer) {
                            self.editor.form.inline_form_footer.toggle(!self.edit_inline_cond);
                        }
                        var focus_field = options && options.focus_field ? options.focus_field : undefined;
                        if (!focus_field) {
                            focus_field = _.find(self.editor.form.fields_order, function (field) {
                                return fields[field] && fields[field].$el.is(':visible:has(input)');
                            });
                        }
                        if (focus_field && fields[focus_field]) fields[focus_field].$el.find('input').select();
                        return record.attributes;
                    });
                }).fail(function () {
                    // if the start_edition event is cancelled and it was a
                    // creation, remove the newly-created empty record
                    if (!record.get('id')) {
                        self.records.remove(record);
                    }
                });
            });
        },
        /**
         * If currently editing a row, resizes all registered form fields based
         * on the corresponding row cell
         */
        resize_fields: function () {
            if (!this.editor.is_editing()) {
                return;
            }
            for (var i = 0, len = this.fields_for_resize.length; i < len; ++i) {
                var item = this.fields_for_resize[i];
                this.resize_field(item.field, item.cell);
            }
            this.$el.find('.oe_form_container.oe_form_nosheet').css({
                'height': '0px',
            });
        },
        /**
         * Resizes a field's root element based on the corresponding cell of
         * a listview row
         *
         * @param {instance.web.form.AbstractField} field
         * @param {jQuery} cell
         */
        resize_field: function (field, cell) {
            var $cell = $(cell);

            field.set_dimensions($cell.outerHeight(), $cell.outerWidth());
            field.$el.css({
                top: 0,
                left: 0
            }).position({
                my: 'left top',
                at: 'left top',
                of: $cell
            });
            if (field.get('effective_readonly')) {
                field.$el.addClass('oe_readonly');
            }
            if (field.widget == "handle")
                field.$el.addClass('oe_list_field_handle');
            field.$el.find('.form-group').css({
                'padding': '0px',
            });
        },
        /**
         * Show edit form instead of inline editing of object
         *
         * @param {jQuery} recordRow
         */
        show_edit_form: function (recordRow) {
            var self = this;
            if (!this.editor.is_editing()) {
                return;
            }
            var target_list = this.$el.find('.table-responsive');
            // Init the form hidden
            self.editor.form.$el.hide();
            if (!self.editor.form.has_responsive_footer) {
                self.add_actions_to_form(self.editor.form.$el);
                self.editor.form.has_responsive_footer = true;
                for (var i = 0, len = this.fields_for_resize.length; i < len; ++i) {
                    var item = this.fields_for_resize[i];
                    item.field.$el.before('<p><b>' + item.field.string + '</b></p>');
                }
            }

            self.editor.form.$el.slideToggle(false);
            target_list.slideToggle().css({
                'overflow-x': 'auto'
            });
            return;
        },
        /**
         * Show actions (Save, Cancel, Delete) buttons in the footer of form
         * 
         * @param {jQuery} $form
         */
        add_actions_to_form: function ($form) {
            var self = this;
            var inline_form_footer = $('<div class="btn-group" role="role" style="width:100% !important;"></div>').append(
                $('<a href="#" class="btn btn-danger" style="color:#fff;">Save</a>').off('click touchstart').on('click touchstart', function (e) {
                    // Save
                    e.preventDefault();
                    self.save_edition();
                    self.$el.find('.table-responsive').slideToggle(function () {
                        $(this).css({
                            'overflow-x': 'auto'
                        });
                    });

                })).append($('<a href="#" class="btn btn-default">Cancel</a>').off('click touchstart').on('click touchstart', function (e) {
                e.preventDefault();
                self.cancel_edition(true);
                self.$el.find('.table-responsive').slideToggle(function () {
                    $(this).css({
                        'overflow-x': 'auto'
                    });
                });

            }));
            $form.append(inline_form_footer);
            self.editor.form.inline_form_footer = inline_form_footer;
            return;
        }
    });
    instance.web.list.Editor.include({
        /**
         * @constructs instance.web.list.Editor
         * @extends instance.web.Widget
         *
         * Adapter between listview and formview for editable-listview purposes
         *
         * @param {instance.web.Widget} parent
         * @param {Object} options
         * @param {instance.web.FormView} [options.formView=instance.web.FormView]
         * @param {Object} [options.delegate]
         */
        init: function (parent, options) {
            this._super(parent);
            this.options = options || {};
            _.defaults(this.options, {
                formView: instance.web.ResponsiveFormView,
                delegate: this.getParent()
            });
            this.delegate = this.options.delegate;

            this.record = null;

            this.form = new(this.options.formView)(
                this, this.delegate.dataset, false, {
                    initial_mode: 'edit',
                    disable_autofocus: true,
                    $buttons: $(),
                    $pager: $()
                });
        },
        edit: function (record, configureField, options) {
            // TODO: specify sequence of edit calls
            var self = this;
            var form = self.form;
            var loaded = record ? form.trigger('load_record', _.extend({}, record)) : form.load_defaults();
            return $.when(loaded).then(function () {
                if (self.edit_inline_cond) {
                    form.$el.find('.oe_form_field').css({
                        'position': 'absolute',
                    });
                }
                return form.do_show({
                    reload: false
                });
            }).then(function () {
                self.record = form.datarecord;
                _(form.fields).each(function (field, name) {
                    configureField(name, field);
                });
                return form;
            });
        },
    });
})();
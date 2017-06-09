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

    instance.web.form.AbstractField.include({
        set_dimensions: function (height, width) {
            this.$el.css({
                width: width,
                minHeight: height,
                maxheight: height,
            });
        },
    });
    instance.web.form.AbstractFormPopup.include({
        template: "AbstractFormPopup.render",
        setup_form_view: function () {
            var self = this;
            if (this.row_id) {
                this.dataset.ids = [this.row_id];
                this.dataset.index = 0;
            } else {
                this.dataset.index = null;
            }
            var options = _.clone(self.options.form_view_options) || {};
            if (this.row_id !== null) {
                options.initial_mode = this.options.readonly ? "view" : "edit";
            }
            _.extend(options, {
                $buttons: this.$buttonpane,
            });
            this.view_form = new instance.web.ResponsiveFormView(this, this.dataset, this.options.view_id || false, options);
            if (this.options.alternative_form_view) {
                this.view_form.set_embedded_view(this.options.alternative_form_view);
            }
            this.view_form.appendTo(this.$el.find(".oe_popup_form"));
            this.view_form.on("form_view_loaded", self, function () {
                var multi_select = self.row_id === null && !self.options.disable_multiple_selection;
                self.$buttonpane.html(QWeb.render("AbstractFormPopup.buttons", {
                    multi_select: multi_select,
                    readonly: self.row_id !== null && self.options.readonly,
                }));
                var $snbutton = self.$buttonpane.find(".oe_abstractformpopup-form-save-new");
                $snbutton.click(function () {
                    $.when(self.view_form.save()).done(function () {
                        self.view_form.reload_mutex.exec(function () {
                            self.view_form.on_button_new();
                        });
                    });
                });
                var $sbutton = self.$buttonpane.find(".oe_abstractformpopup-form-save");
                $sbutton.click(function () {
                    $.when(self.view_form.save()).done(function () {
                        self.view_form.reload_mutex.exec(function () {
                            self.check_exit();
                        });
                    });
                });
                var $cbutton = self.$buttonpane.find(".oe_abstractformpopup-form-close");
                $cbutton.click(function () {
                    self.view_form.trigger('on_button_cancel');
                    self.check_exit();
                });
                self.view_form.do_show();
            });
        },
    });
    instance.web.views.add('form', 'instance.web.ResponsiveFormView');
    instance.web.ResponsiveFormView = instance.web.FormView.extend({
        /**
         * Indicates that this view is not searchable, and thus that no search
         * view should be displayed (if there is one active).
         */
        searchable: false,
        template: "ResponsiveFormView",
        display_name: _lt('Form'),
        view_type: "form",
        init: function () {
            this._super.apply(this, arguments);
            this.rendering_engine = new instance.web.form.ResponsiveFormRenderingEngine(this);
        },
        view_loading: function (r) {
            return this.load_form(r);
        },
        destroy: function () {
            _.each(this.get_widgets(), function (w) {
                w.off('focused blurred');
                w.destroy();
            });
            if (this.$el) {
                this.$el.off('.formBlur');
            }
            this._super();
        },
        load_form: function (data) {
            var self = this;
            if (!data) {
                throw new Error(_t("No data provided."));
            }
            if (this.arch) {
                throw "Form view does not support multiple calls to load_form";
            }
            this.fields_order = [];
            this.fields_view = data;

            this.rendering_engine.set_fields_registry(this.fields_registry);
            this.rendering_engine.set_tags_registry(this.tags_registry);
            this.rendering_engine.set_widgets_registry(this.widgets_registry);
            this.rendering_engine.set_fields_view(data);
            var $dest = this.$el.hasClass("oe_form_container") ? this.$el : this.$el.find('.oe_form_container');
            this.rendering_engine.render_to($dest);

            this.$el.on('mousedown.formBlur', function () {
                self.__clicked_inside = true;
            });

            this.$buttons = $(QWeb.render("ResponsiveFormView.buttons", {'widget': self}));
            if (this.options.$buttons) {
                this.$buttons.appendTo(this.options.$buttons);
            } else {
                this.$el.find('.oe_form_buttons').replaceWith(this.$buttons);
            }
            this.$buttons.on('click', '.oe_form_button_create',
                    this.guard_active(this.on_button_create));
            this.$buttons.on('click', '.oe_form_button_edit',
                    this.guard_active(this.on_button_edit));
            this.$buttons.on('click', '.oe_form_button_save',
                    this.guard_active(this.on_button_save));
            this.$buttons.on('click', '.oe_form_button_cancel',
                    this.guard_active(this.on_button_cancel));
            if (this.options.footer_to_buttons) {
                this.$el.find('footer').appendTo(this.$buttons);
            }

            this.$sidebar = this.options.$sidebar || this.$el.find('.oe_form_sidebar');
            if (!this.sidebar && this.options.$sidebar) {
                this.sidebar = new instance.web.Sidebar(this);
                this.sidebar.appendTo(this.$sidebar);
                if (this.fields_view.toolbar) {
                    this.sidebar.add_toolbar(this.fields_view.toolbar);
                }
                this.sidebar.add_items('other', _.compact([
                    self.is_action_enabled('delete') && {label: _t('Delete'), callback: self.on_button_delete},
                    self.is_action_enabled('create') && {label: _t('Duplicate'), callback: self.on_button_duplicate}
                ]));
            }

            this.has_been_loaded.resolve();

            // Add bounce effect on button 'Edit' when click on readonly page view.
            this.$el.find(".oe_form_group_row,.oe_form_field,label,h1,.oe_title,.oe_notebook_page, .oe_list_content").on('click', function (e) {
                if (self.get("actual_mode") == "view") {
                    var $button = self.options.$buttons.find(".oe_form_button_edit");
                    $button.openerpBounce();
                    e.stopPropagation();
                    instance.web.bus.trigger('click', e);
                }
            });
            //bounce effect on red button when click on statusbar.
            this.$el.find(".oe_form_field_status:not(.oe_form_status_clickable)").on('click', function (e) {
                if ((self.get("actual_mode") == "view")) {
                    var $button = self.$el.find(".oe_highlight:not(.oe_form_invisible)").css({'float': 'left', 'clear': 'none'});
                    $button.openerpBounce();
                    e.stopPropagation();
                }
            });
            this.trigger('form_view_loaded', data);
            return $.when();
        },
        widgetFocused: function () {
            // Clear click flag if used to focus a widget
            this.__clicked_inside = false;
            if (this.__blur_timeout) {
                clearTimeout(this.__blur_timeout);
                this.__blur_timeout = null;
            }
        },
        widgetBlurred: function () {
            if (this.__clicked_inside) {
                // clicked in an other section of the form (than the currently
                // focused widget) => just ignore the blurring entirely?
                this.__clicked_inside = false;
                return;
            }
            var self = this;
            // clear timeout, if any
            this.widgetFocused();
            this.__blur_timeout = setTimeout(function () {
                self.trigger('blurred');
            }, 0);
        },
        do_load_state: function (state, warm) {
            if (state.id && this.datarecord.id != state.id) {
                if (this.dataset.get_id_index(state.id) === null) {
                    this.dataset.ids.push(state.id);
                }
                this.dataset.select_id(state.id);
                this.do_show();
            }
        },
        /**
         *
         * @param {Object} [options]
         * @param {Boolean} [mode=undefined] If specified, switch the form to specified mode. Can be "edit" or "view".
         * @param {Boolean} [reload=true] whether the form should reload its content on show, or use the currently loaded record
         * @return {$.Deferred}
         */
        do_show: function (options) {
            var self = this;
            options = options || {};
            if (this.sidebar) {
                this.sidebar.$el.show();
            }
            if (this.$buttons) {
                this.$buttons.show();
            }
            this.$el.show().css({
                opacity: '0',
                filter: 'alpha(opacity = 0)'
            });
            this.$el.add(this.$buttons).removeClass('oe_form_dirty');

            var shown = this.has_been_loaded;
            if (options.reload !== false) {
                shown = shown.then(function () {
                    if (self.dataset.index === null) {
                        // null index means we should start a new record
                        return self.on_button_new();
                    }
                    var fields = _.keys(self.fields_view.fields);
                    fields.push('display_name');
                    return self.dataset.read_index(fields, {
                        context: {'bin_size': true}
                    }).then(function (r) {
                        self.trigger('load_record', r);
                    });
                });
            }
            return shown.then(function () {
                self._actualize_mode(options.mode || self.options.initial_mode);
                self.$el.css({
                    opacity: '1',
                    filter: 'alpha(opacity = 100)'
                });
            });
        },
        do_hide: function () {
            if (this.sidebar) {
                this.sidebar.$el.hide();
            }
            if (this.$buttons) {
                this.$buttons.hide();
            }
            if (this.$pager) {
                this.$pager.hide();
            }
            this._super();
        },
        load_record: function (record) {
            var self = this, set_values = [];
            if (!record) {
                this.set({'title': undefined});
                this.do_warn(_t("Form"), _t("The record could not be found in the database."), true);
                return $.Deferred().reject();
            }
            this.datarecord = record;
            this._actualize_mode();
            this.set({'title': record.id ? record.display_name : _t("New")});

            _(this.fields).each(function (field, f) {
                field._dirty_flag = false;
                field._inhibit_on_change_flag = true;
                var result = field.set_value(self.datarecord[f] || false);
                field._inhibit_on_change_flag = false;
                set_values.push(result);
            });
            return $.when.apply(null, set_values).then(function () {
                if (!record.id) {
                    // trigger onchanges
                    self.do_onchange(null);
                }
                self.on_form_changed();
                self.rendering_engine.init_fields();
                self.is_initialized.resolve();
                self.do_update_pager(record.id === null || record.id === undefined);
                if (self.sidebar) {
                    self.sidebar.do_attachement_update(self.dataset, self.datarecord.id);
                }
                if (record.id) {
                    self.do_push_state({id: record.id});
                } else {
                    self.do_push_state({});
                }
                self.$el.add(self.$buttons).removeClass('oe_form_dirty');
                self.autofocus();
            });
        },
        /**
         * Loads and sets up the default values for the model as the current
         * record
         *
         * @return {$.Deferred}
         */
        load_defaults: function () {
            var self = this;
            var keys = _.keys(this.fields_view.fields);
            if (keys.length) {
                return this.dataset.default_get(keys).then(function (r) {
                    self.trigger('load_record', r);
                });
            }
            return self.trigger('load_record', {});
        },
        on_form_changed: function () {
            this.trigger("view_content_has_changed");
        },
        do_notify_change: function () {
            this.$el.add(this.$buttons).addClass('oe_form_dirty');
        },
        execute_pager_action: function (action) {
            if (this.can_be_discarded()) {
                switch (action) {
                    case 'first':
                        this.dataset.index = 0;
                        break;
                    case 'previous':
                        this.dataset.previous();
                        break;
                    case 'next':
                        this.dataset.next();
                        break;
                    case 'last':
                        this.dataset.index = this.dataset.ids.length - 1;
                        break;
                }
                var def = this.reload();
                this.trigger('pager_action_executed');
                return def;
            }
            return $.when();
        },
        init_pager: function () {
            var self = this;
            if (this.$pager)
                this.$pager.remove();
            if (this.get("actual_mode") === "create")
                return;
            this.$pager = $(QWeb.render("ResponsiveFormView.pager", {'widget': self})).hide();
            if (this.options.$pager) {
                this.$pager.appendTo(this.options.$pager);
            } else {
                this.$el.find('.oe_form_pager').replaceWith(this.$pager);
            }
            this.$pager.on('click', 'a[data-pager-action]', function () {
                var $el = $(this);
                if ($el.attr("disabled"))
                    return;
                var action = $el.data('pager-action');
                var def = $.when(self.execute_pager_action(action));
                $el.attr("disabled");
                def.always(function () {
                    $el.removeAttr("disabled");
                });
            });
            this.do_update_pager();
        },
        do_update_pager: function (hide_index) {
            this.$pager.toggle(this.dataset.ids.length > 1);
            if (hide_index) {
                $(".oe_form_pager_state", this.$pager).html("");
            } else {
                $(".oe_form_pager_state", this.$pager).html(_.str.sprintf(_t("%d / %d"), this.dataset.index + 1, this.dataset.ids.length));
            }
        },
        _build_onchange_specs: function () {
            var self = this;
            var find = function (field_name, root) {
                var fields = [root];
                while (fields.length) {
                    var node = fields.pop();
                    if (!node) {
                        continue;
                    }
                    if (node.tag === 'field' && node.attrs.name === field_name) {
                        return node.attrs.on_change || "";
                    }
                    fields = _.union(fields, node.children);
                }
                return "";
            };

            self._onchange_fields = [];
            self._onchange_specs = {};
            _.each(this.fields, function (field, name) {
                self._onchange_fields.push(name);
                self._onchange_specs[name] = find(name, field.node);
                _.each(field.field.views, function (view) {
                    _.each(view.fields, function (_, subname) {
                        self._onchange_specs[name + '.' + subname] = find(subname, view.arch);
                    });
                });
            });
        },
        _get_onchange_values: function () {
            var field_values = this.get_fields_values();
            if (field_values.id.toString().match(instance.web.BufferedDataSet.virtual_id_regex)) {
                delete field_values.id;
            }
            if (this.dataset.parent_view) {
                // this belongs to a parent view: add parent field if possible
                var parent_view = this.dataset.parent_view;
                var child_name = this.dataset.child_name;
                var parent_name = parent_view.get_field_desc(child_name).relation_field;
                if (parent_name) {
                    // consider all fields except the inverse of the parent field
                    var parent_values = parent_view.get_fields_values();
                    delete parent_values[child_name];
                    field_values[parent_name] = parent_values;
                }
            }
            return field_values;
        },
        do_onchange: function (widget) {
            var self = this;
            var onchange_specs = self._onchange_specs;
            try {
                var def = $.when({});
                var change_spec = widget ? onchange_specs[widget.name] : null;
                if (!widget || (!_.isEmpty(change_spec) && change_spec !== "0")) {
                    var ids = [],
                            trigger_field_name = widget ? widget.name : self._onchange_fields,
                            values = self._get_onchange_values(),
                            context = new instance.web.CompoundContext(self.dataset.get_context());

                    if (widget && widget.build_context()) {
                        context.add(widget.build_context());
                    }
                    if (self.dataset.parent_view) {
                        var parent_name = self.dataset.parent_view.get_field_desc(self.dataset.child_name).relation_field;
                        context.add({field_parent: parent_name});
                    }

                    if (self.datarecord.id && !instance.web.BufferedDataSet.virtual_id_regex.test(self.datarecord.id)) {
                        // In case of a o2m virtual id, we should pass an empty ids list
                        ids.push(self.datarecord.id);
                    }
                    def = self.alive(new instance.web.Model(self.dataset.model).call(
                            "onchange", [ids, values, trigger_field_name, onchange_specs, context]));
                }
                this.onchanges_mutex.exec(function () {
                    return def.then(function (response) {
                        var fields = {};
                        if (widget) {
                            fields[widget.name] = widget.field;
                        }
                        else {
                            fields = self.fields_view.fields;
                        }
                        var defs = [];
                        _.each(fields, function (field, fieldname) {
                            if (field && field.change_default) {
                                var value_;
                                if (response.value && (fieldname in response.value)) {
                                    // Use value from onchange if onchange executed
                                    value_ = response.value[fieldname];
                                } else {
                                    // otherwise get form value for field
                                    value_ = self.fields[fieldname].get_value();
                                }
                                var condition = fieldname + '=' + value_;

                                if (value_) {
                                    defs.push(self.alive(new instance.web.Model('ir.values').call(
                                            'get_defaults', [self.model, condition]
                                            )).then(function (results) {
                                        if (!results.length) {
                                            return response;
                                        }
                                        if (!response.value) {
                                            response.value = {};
                                        }
                                        for (var i = 0; i < results.length; ++i) {
                                            // [whatever, key, value]
                                            var triplet = results[i];
                                            response.value[triplet[1]] = triplet[2];
                                        }
                                        return response;
                                    }));
                                }
                            }
                        });
                        return _.isEmpty(defs) ? response : $.when.apply(null, defs);
                    }).then(function (response) {
                        return self.on_processed_onchange(response);
                    });
                });
                return this.onchanges_mutex.def;
            } catch (e) {
                console.error(e);
                instance.webclient.crashmanager.show_message(e);
                return $.Deferred().reject();
            }
        },
        on_processed_onchange: function (result) {
            try {
                var fields = this.fields;
                _(result.domain).each(function (domain, fieldname) {
                    var field = fields[fieldname];
                    if (!field) {
                        return;
                    }
                    field.node.attrs.domain = domain;
                });

                if (!_.isEmpty(result.value)) {
                    this._internal_set_values(result.value);
                }
                // FIXME XXX a list of warnings?
                if (!_.isEmpty(result.warning)) {
                    new instance.web.Dialog(this, {
                        size: 'medium',
                        title: result.warning.title,
                        buttons: [
                            {text: _t("Ok"), click: function () {
                                    this.parents('.modal').modal('hide');
                                }}
                        ]
                    }, QWeb.render("CrashManager.warning", result.warning)).open();
                }

                return $.Deferred().resolve();
            } catch (e) {
                console.error(e);
                instance.webclient.crashmanager.show_message(e);
                return $.Deferred().reject();
            }
        },
        _process_operations: function () {
            var self = this;
            return this.mutating_mutex.exec(function () {
                function iterate() {

                    var mutex = new $.Mutex();
                    _.each(self.fields, function (field) {
                        self.onchanges_mutex.def.then(function () {
                            mutex.exec(function () {
                                return field.commit_value();
                            });
                        });
                    });

                    var args = _.toArray(arguments);
                    return $.when.apply(null, [mutex.def, self.onchanges_mutex.def]).then(function () {
                        var save_obj = self.save_list.pop();
                        if (save_obj) {
                            return self._process_save(save_obj).then(function () {
                                save_obj.ret = _.toArray(arguments);
                                return iterate();
                            }, function () {
                                save_obj.error = true;
                            });
                        }
                        return $.when();
                    }).fail(function () {
                        self.save_list.pop();
                        return $.when();
                    });
                }
                return iterate();
            });
        },
        _internal_set_values: function (values) {
            for (var f in values) {
                if (!values.hasOwnProperty(f)) {
                    continue;
                }
                var field = this.fields[f];
                // If field is not defined in the view, just ignore it
                if (field) {
                    var value_ = values[f];
                    if (field.get_value() != value_) {
                        field._inhibit_on_change_flag = true;
                        field.set_value(value_);
                        field._inhibit_on_change_flag = false;
                        field._dirty_flag = true;
                    }
                }
            }
            this.on_form_changed();
        },
        set_values: function (values) {
            var self = this;
            return this.mutating_mutex.exec(function () {
                self._internal_set_values(values);
            });
        },
        /**
         * Ask the view to switch to view mode if possible. The view may not do it
         * if the current record is not yet saved. It will then stay in create mode.
         */
        to_view_mode: function () {
            this._actualize_mode("view");
        },
        /**
         * Ask the view to switch to edit mode if possible. The view may not do it
         * if the current record is not yet saved. It will then stay in create mode.
         */
        to_edit_mode: function () {
            this.onchanges_mutex = new $.Mutex();
            this._actualize_mode("edit");
        },
        /**
         * Ask the view to switch to a precise mode if possible. The view is free to
         * not respect this command if the state of the dataset is not compatible with
         * the new mode. For example, it is not possible to switch to edit mode if
         * the current record is not yet saved in database.
         *
         * @param {string} [new_mode] Can be "edit", "view", "create" or undefined. If
         * undefined the view will test the actual mode to check if it is still consistent
         * with the dataset state.
         */
        _actualize_mode: function (switch_to) {
            var mode = switch_to || this.get("actual_mode");
            if (!this.datarecord.id) {
                mode = "create";
            } else if (mode === "create") {
                mode = "edit";
            }
            this.render_value_defs = [];
            this.set({actual_mode: mode});
        },
        check_actual_mode: function (source, options) {
            var self = this;

            if (this.get("actual_mode") === "view") {
                self.$el.removeClass('oe_form_editable').addClass('oe_form_readonly');
                self.$buttons.find('.oe_form_buttons_edit').hide();
                self.$buttons.find('.oe_form_buttons_view').show();
                self.$sidebar.show();
            } else {
                self.$el.removeClass('oe_form_readonly').addClass('oe_form_editable');
                self.$buttons.find('.oe_form_buttons_edit').show();
                self.$buttons.find('.oe_form_buttons_view').hide();
                self.$sidebar.hide();
                this.autofocus();
            }
        },
        autofocus: function () {
            if (this.get("actual_mode") !== "view" && !this.options.disable_autofocus) {
                var fields_order = this.fields_order.slice(0);
                if (this.default_focus_field) {
                    fields_order.unshift(this.default_focus_field.name);
                }
                for (var i = 0; i < fields_order.length; i += 1) {
                    var field = this.fields[fields_order[i]];
                    if (!field.get('effective_invisible') && !field.get('effective_readonly') && field.$label) {
                        if (field.focus() !== false) {
                            break;
                        }
                    }
                }
            }
        },
        on_button_save: function (e) {
            var self = this;
            $(e.target).attr("disabled", true);
            return this.save().done(function (result) {
                self.trigger("save", result);
                self.reload().then(function () {
                    self.to_view_mode();
                    var menu = instance.webclient.menu;
                    if (menu) {
                        menu.do_reload_needaction();
                    }
                });
            }).always(function () {
                $(e.target).attr("disabled", false);
            });
        },
        on_button_cancel: function (event) {
            var self = this;
            if (this.can_be_discarded()) {
                if (this.get('actual_mode') === 'create') {
                    this.trigger('history_back');
                } else {
                    this.to_view_mode();
                    $.when.apply(null, this.render_value_defs).then(function () {
                        self.trigger('load_record', self.datarecord);
                    });
                }
            }
            this.trigger('on_button_cancel');
            return false;
        },
        on_button_new: function () {
            var self = this;
            this.to_edit_mode();
            return $.when(this.has_been_loaded).then(function () {
                if (self.can_be_discarded()) {
                    return self.load_defaults();
                }
            });
        },
        on_button_edit: function () {
            return this.to_edit_mode();
        },
        on_button_create: function () {
            this.dataset.index = null;
            this.do_show();
        },
        on_button_duplicate: function () {
            var self = this;
            return this.has_been_loaded.then(function () {
                return self.dataset.call('copy', [self.datarecord.id, {}, self.dataset.context]).then(function (new_id) {
                    self.record_created(new_id);
                    self.to_edit_mode();
                });
            });
        },
        on_button_delete: function () {
            var self = this;
            var def = $.Deferred();
            this.has_been_loaded.done(function () {
                if (self.datarecord.id && confirm(_t("Do you really want to delete this record?"))) {
                    self.dataset.unlink([self.datarecord.id]).done(function () {
                        if (self.dataset.size()) {
                            self.execute_pager_action('next');
                        } else {
                            self.do_action('history_back');
                        }
                        def.resolve();
                    });
                } else {
                    $.async_when().done(function () {
                        def.reject();
                    });
                }
            });
            return def.promise();
        },
        can_be_discarded: function () {
            if (this.$el.is('.oe_form_dirty')) {
                if (!confirm(_t("Warning, the record has been modified, your changes will be discarded.\n\nAre you sure you want to leave this page ?"))) {
                    return false;
                }
                this.$el.removeClass('oe_form_dirty');
            }
            return true;
        },
        /**
         * Triggers saving the form's record. Chooses between creating a new
         * record or saving an existing one depending on whether the record
         * already has an id property.
         *
         * @param {Boolean} [prepend_on_create=false] if ``save`` creates a new
         * record, should that record be inserted at the start of the dataset (by
         * default, records are added at the end)
         */
        save: function (prepend_on_create) {
            var self = this;
            var save_obj = {prepend_on_create: prepend_on_create, ret: null};
            this.save_list.push(save_obj);
            return self._process_operations().then(function () {
                if (save_obj.error)
                    return $.Deferred().reject();
                return $.when.apply($, save_obj.ret);
            }).done(function (result) {
                self.$el.removeClass('oe_form_dirty');
            });
        },
        _process_save: function (save_obj) {
            var self = this;
            var prepend_on_create = save_obj.prepend_on_create;
            try {
                var form_invalid = false,
                        values = {},
                        first_invalid_field = null,
                        readonly_values = {};
                for (var f in self.fields) {
                    if (!self.fields.hasOwnProperty(f)) {
                        continue;
                    }
                    f = self.fields[f];
                    if (!f.is_valid()) {
                        form_invalid = true;
                        if (!first_invalid_field) {
                            first_invalid_field = f;
                        }
                    } else if (f.name !== 'id' && (!self.datarecord.id || f._dirty_flag)) {
                        // Special case 'id' field, do not save this field
                        // on 'create' : save all non readonly fields
                        // on 'edit' : save non readonly modified fields
                        if (!f.get("readonly")) {
                            values[f.name] = f.get_value();
                        } else {
                            readonly_values[f.name] = f.get_value();
                        }
                    }
                }
                // Heuristic to assign a proper sequence number for new records that
                // are added in a dataset containing other lines with existing sequence numbers
                if (!self.datarecord.id && self.fields.sequence &&
                        !_.has(values, 'sequence') && !_.isEmpty(self.dataset.cache)) {
                    // Find current max or min sequence (editable top/bottom)
                    var current = _[prepend_on_create ? "min" : "max"](
                            _.map(self.dataset.cache, function (o) {
                                return o.values.sequence
                            })
                            );
                    values['sequence'] = prepend_on_create ? current - 1 : current + 1;
                }
                if (form_invalid) {
                    self.set({'display_invalid_fields': true});
                    first_invalid_field.focus();
                    self.on_invalid();
                    return $.Deferred().reject();
                } else {
                    self.set({'display_invalid_fields': false});
                    var save_deferral;
                    if (!self.datarecord.id) {
                        // Creation save
                        save_deferral = self.dataset.create(values, {readonly_fields: readonly_values}).then(function (r) {
                            return self.record_created(r, prepend_on_create);
                        }, null);
                    } else if (_.isEmpty(values)) {
                        // Not dirty, noop save
                        save_deferral = $.Deferred().resolve({}).promise();
                    } else {
                        // Write save
                        save_deferral = self.dataset.write(self.datarecord.id, values, {readonly_fields: readonly_values}).then(function (r) {
                            return self.record_saved(r);
                        }, null);
                    }
                    return save_deferral;
                }
            } catch (e) {
                console.error(e);
                return $.Deferred().reject();
            }
        },
        on_invalid: function () {
            var warnings = _(this.fields).chain()
                    .filter(function (f) {
                        return !f.is_valid();
                    })
                    .map(function (f) {
                        return _.str.sprintf('<li>%s</li>',
                                _.escape(f.string));
                    }).value();
            warnings.unshift('<ul>');
            warnings.push('</ul>');
            this.do_warn(_t("The following fields are invalid:"), warnings.join(''));
        },
        /**
         * Reload the form after saving
         *
         * @param {Object} r result of the write function.
         */
        record_saved: function (r) {
            this.trigger('record_saved', r);
            if (!r) {
                // should not happen in the server, but may happen for internal purpose
                return $.Deferred().reject();
            }
            return r;
        },
        /**
         * Updates the form' dataset to contain the new record:
         *
         * * Adds the newly created record to the current dataset (at the end by
         *   default)
         * * Selects that record (sets the dataset's index to point to the new
         *   record's id).
         * * Updates the pager and sidebar displays
         *
         * @param {Object} r
         * @param {Boolean} [prepend_on_create=false] adds the newly created record
         * at the beginning of the dataset instead of the end
         */
        record_created: function (r, prepend_on_create) {
            var self = this;
            if (!r) {
                // should not happen in the server, but may happen for internal purpose
                this.trigger('record_created', r);
                return $.Deferred().reject();
            } else {
                this.datarecord.id = r;
                if (!prepend_on_create) {
                    this.dataset.alter_ids(this.dataset.ids.concat([this.datarecord.id]));
                    this.dataset.index = this.dataset.ids.length - 1;
                } else {
                    this.dataset.alter_ids([this.datarecord.id].concat(this.dataset.ids));
                    this.dataset.index = 0;
                }
                this.do_update_pager();
                if (this.sidebar) {
                    this.sidebar.do_attachement_update(this.dataset, this.datarecord.id);
                }
                //openerp.log("The record has been created with id #" + this.datarecord.id);
                return $.when(this.reload()).then(function () {
                    self.trigger('record_created', r);
                    return _.extend(r, {created: true});
                });
            }
        },
        on_action: function (action) {
            console.debug('Executing action', action);
        },
        reload: function () {
            var self = this;
            return this.reload_mutex.exec(function () {
                if (self.dataset.index === null || self.dataset.index === undefined) {
                    self.trigger("previous_view");
                    return $.Deferred().reject().promise();
                }
                if (self.dataset.index < 0) {
                    return $.when(self.on_button_new());
                } else {
                    var fields = _.keys(self.fields_view.fields);
                    fields.push('display_name');
                    return self.dataset.read_index(fields,
                            {
                                context: {'bin_size': true},
                                check_access_rule: true
                            }).then(function (r) {
                        self.trigger('load_record', r);
                    }).fail(function () {
                        self.do_action('history_back');
                    });
                }
            });
        },
        get_widgets: function () {
            return _.filter(this.getChildren(), function (obj) {
                return obj instanceof instance.web.form.FormWidget;
            });
        },
        get_fields_values: function () {
            var values = {};
            var ids = this.get_selected_ids();
            values["id"] = ids.length > 0 ? ids[0] : false;
            _.each(this.fields, function (value_, key) {
                values[key] = value_.get_value();
            });
            return values;
        },
        get_selected_ids: function () {
            var id = this.dataset.ids[this.dataset.index];
            return id ? [id] : [];
        },
        recursive_save: function () {
            var self = this;
            return $.when(this.save()).then(function (res) {
                if (self.dataset.parent_view)
                    return self.dataset.parent_view.recursive_save();
            });
        },
        recursive_reload: function () {
            var self = this;
            var pre = $.when();
            if (self.dataset.parent_view)
                pre = self.dataset.parent_view.recursive_reload();
            return pre.then(function () {
                return self.reload();
            });
        },
        is_dirty: function () {
            return _.any(this.fields, function (value_) {
                return value_._dirty_flag;
            });
        },
        is_interactible_record: function () {
            var id = this.datarecord.id;
            if (!id) {
                if (this.options.not_interactible_on_create)
                    return false;
            } else if (typeof (id) === "string") {
                if (instance.web.BufferedDataSet.virtual_id_regex.test(id))
                    return false;
            }
            return true;
        },
        sidebar_eval_context: function () {
            return $.when(this.build_eval_context());
        },
        open_defaults_dialog: function () {
            var self = this;
            var display = function (field, value) {
                if (!value) {
                    return value;
                }
                if (field instanceof instance.web.form.FieldSelection) {
                    return _(field.get('values')).find(function (option) {
                        return option[0] === value;
                    })[1];
                } else if (field instanceof instance.web.form.FieldMany2One) {
                    return field.get_displayed();
                }
                return value;
            };
            var fields = _.chain(this.fields)
                    .map(function (field) {
                        var value = field.get_value();
                        // ignore fields which are empty, invisible, readonly, o2m
                        // or m2m
                        if (!value
                                || field.get('invisible')
                                || field.get("readonly")
                                || field.field.type === 'one2many'
                                || field.field.type === 'many2many'
                                || field.field.type === 'binary'
                                || field.password) {
                            return false;
                        }

                        return {
                            name: field.name,
                            string: field.string,
                            value: value,
                            displayed: display(field, value),
                        };
                    })
                    .compact()
                    .sortBy(function (field) {
                        return field.string;
                    })
                    .value();
            var conditions = _.chain(self.fields)
                    .filter(function (field) {
                        return field.field.change_default;
                    })
                    .map(function (field) {
                        var value = field.get_value();
                        return {
                            name: field.name,
                            string: field.string,
                            value: value,
                            displayed: display(field, value),
                        };
                    })
                    .value();
            var d = new instance.web.Dialog(this, {
                title: _t("Set Default"),
                args: {
                    fields: fields,
                    conditions: conditions
                },
                buttons: [
                    {text: _t("Close"), click: function () {
                            d.close();
                        }},
                    {text: _t("Save default"), click: function () {
                            var $defaults = d.$el.find('#formview_default_fields');
                            var field_to_set = $defaults.val();
                            if (!field_to_set) {
                                $defaults.parent().addClass('oe_form_invalid');
                                $defaults.parent().addClass('has-feedback has-error');
                                return;
                            }
                            var condition = d.$el.find('#formview_default_conditions').val(),
                                    all_users = d.$el.find('#formview_default_all').is(':checked');
                            new instance.web.DataSet(self, 'ir.values').call(
                                    'set_default', [
                                        self.dataset.model,
                                        field_to_set,
                                        self.fields[field_to_set].get_value(),
                                        all_users,
                                        true,
                                        condition || false
                                    ]).done(function () {
                                d.close();
                            });
                        }}
                ]
            });
            d.template = 'FormView.set_default';
            d.open();
        },
        register_field: function (field, name) {
            this.fields[name] = field;
            this.fields_order.push(name);
            if (JSON.parse(field.node.attrs.default_focus || "0")) {
                this.default_focus_field = field;
            }

            field.on('focused', null, this.proxy('widgetFocused'))
                    .on('blurred', null, this.proxy('widgetBlurred'));
            if (this.get_field_desc(name).translate) {
                this.translatable_fields.push(field);
            }
            field.on('changed_value', this, function () {
                if (field.is_syntax_valid()) {
                    this.trigger('field_changed:' + name);
                }
                if (field._inhibit_on_change_flag) {
                    return;
                }
                field._dirty_flag = true;
                if (field.is_syntax_valid()) {
                    this.do_onchange(field);
                    this.on_form_changed(true);
                    this.do_notify_change();
                }
            });
        },
        get_field_desc: function (field_name) {
            return this.fields_view.fields[field_name];
        },
        get_field_value: function (field_name) {
            return this.fields[field_name].get_value();
        },
        compute_domain: function (expression) {
            return instance.web.form.compute_domain(expression, this.fields);
        },
        _build_view_fields_values: function () {
            var a_dataset = this.dataset;
            var fields_values = this.get_fields_values();
            var active_id = a_dataset.ids[a_dataset.index];
            _.extend(fields_values, {
                active_id: active_id || false,
                active_ids: active_id ? [active_id] : [],
                active_model: a_dataset.model,
                parent: {}
            });
            if (a_dataset.parent_view) {
                fields_values.parent = a_dataset.parent_view.get_fields_values();
            }
            return fields_values;
        },
        build_eval_context: function () {
            var a_dataset = this.dataset;
            return new instance.web.CompoundContext(a_dataset.get_context(), this._build_view_fields_values());
        },
    });


    instance.web.form.ResponsiveFormRenderingEngine = instance.web.form.FormRenderingEngine.extend({
        render_to: function ($target) {
            var self = this;
            this.$target = $target;

            this.$form = this.get_arch_fragment();

            this.process_version();

            this.fields_to_init = [];
            this.tags_to_init = [];
            this.widgets_to_init = [];
            this.labels = {};
            this.process(this.$form);

            this.$form.appendTo(this.$target);
            this.to_replace = [];

            _.each(this.fields_to_init, function ($elem) {
                var name = $elem.attr("name");
                if (!self.fvg.fields[name]) {
                    throw new Error(_.str.sprintf(_t("Field '%s' specified in view could not be found."), name));
                }
                var obj = self.fields_registry.get_any([$elem.attr('widget'), self.fvg.fields[name].type]);
                if (!obj) {
                    throw new Error(_.str.sprintf(_t("Widget type '%s' is not implemented"), $elem.attr('widget')));
                }
                var w = new (obj)(self.view, instance.web.xml_to_json($elem[0]));
                var $label = self.labels[$elem.attr("name")];
                if ($label) {
                    w.set_input_id($label.attr("for"));
                }
                self.alter_field(w);
                self.view.register_field(w, $elem.attr("name"));
                self.to_replace.push([w, $elem]);
            });
            _.each(this.tags_to_init, function ($elem) {
                var tag_name = $elem[0].tagName.toLowerCase();
                var obj = self.tags_registry.get_object(tag_name);
                var w = new (obj)(self.view, instance.web.xml_to_json($elem[0]));
                self.to_replace.push([w, $elem]);
            });
            _.each(this.widgets_to_init, function ($elem) {
                var widget_type = $elem.attr("type");
                var obj = self.widgets_registry.get_object(widget_type);
                var w = new (obj)(self.view, instance.web.xml_to_json($elem[0]));
                self.to_replace.push([w, $elem]);
            });
            if(this.$target.find('.r_notebook_wrapper').length !==0 ){
              var $n_wrapper = this.$target.find('.r_notebook_wrapper');
              var $notebook = $n_wrapper.find('ul.oe_notebook');
              var $tabs_wrapper = $notebook.wrap($('<div></div>').addClass('r_tabs_wrapper'));
            }
            if(this.$target.find('.oe_button_box [widget="website_button"]').length !==0 ){
              this.$target.find('.oe_button_box [widget="website_button"]').insertAfter('.oe_button_box');
            }
            if((this.$target.find('.oe_button_box').length !==0 )
               && (this.$target.find('.oe_button_box').parents('.oe_button_box_wrapper').length === 0)){
                this.$target.find('.oe_button_box').wrap($('<div></div>').addClass('oe_button_box_wrapper'));
                var $wrapper = this.$target.find('.oe_button_box_wrapper');
                var $button_box = $wrapper.find('.oe_button_box');
                $wrapper.css({
                    'width': '100%',
                    'min-width': '100%',
                    'position': 'absolute',
                    'top': '0',
                    'left': '0',
                    'height': '41px',
//                     'overflow': 'hidden',
                    'padding': '0px 25px',
                });
            }

        },
        attach_node_attr: function($new_element, $node, attr) {
            $new_element.data(attr, $node.attr(attr));
        },
        process_group: function($group) {
            var self = this;
            $group.children('field').each(function() {
                self.preprocess_field($(this));
            });
            var $new_group = this.render_element('FormRenderingGroup', $group.getAttributes());
            var $table;
            if ($new_group.first().is('table.oe_form_group')) {
                $table = $new_group;
            } else if ($new_group.filter('table.oe_form_group').length) {
                $table = $new_group.filter('table.oe_form_group').first();
            } else {
                $table = $new_group.find('table.oe_form_group').first();
            }

            var $tr, $td,
                cols = parseInt($group.attr('col') || 2, 10),
                row_cols = cols;

            var children = [];

            $group.children().each(function(a,b,c) {
                var $child = $(this);
                var colspan = parseInt($child.attr('colspan') || 1, 10);
                var tagName = $child[0].tagName.toLowerCase();
                var $td = $('<td/>').addClass('oe_form_group_cell').attr('colspan', colspan);
                var newline = tagName === 'newline';

                // add flag for ground level groups
                if(tagName ==='group' && $child.children('group').length == 0){
                    $td.addClass('oe_ground_group');
                }

                // Note FME: those classes are used in layout debug mode
                if ($tr && row_cols > 0 && (newline || row_cols < colspan)) {
                    $tr.addClass('oe_form_group_row_incomplete');
                    if (newline) {
                        $tr.addClass('oe_form_group_row_newline');
                    }
                }
                if (newline) {
                    $tr = null;
                    return;
                }
                if (!$tr || row_cols < colspan) {
                    $tr = $('<tr/>').addClass('oe_form_group_row').appendTo($table);
                    row_cols = cols;
                } else if (tagName==='group') {
                    // When <group> <group/><group/> </group>, we need a spacing between the two groups
                    $td.addClass('oe_group_right');
                }
                row_cols -= colspan;

                // invisibility transfer
                var field_modifiers = JSON.parse($child.attr('modifiers') || '{}');
                var invisible = field_modifiers.invisible;
                self.handle_common_properties($td, $("<dummy>").attr("modifiers", JSON.stringify({invisible: invisible})));

                $tr.append($td.append($child));
                children.push($child[0]);
            });
            if (row_cols && $td) {
                $td.attr('colspan', parseInt($td.attr('colspan'), 10) + row_cols);
            }
            $group.before($new_group).remove();

            $table.find('> tbody > tr').each(function() {
                var to_compute = [],
                    row_cols = cols,
                    total = 100;
                $(this).children().each(function() {
                    var $td = $(this),
                        $child = $td.children(':first');
                    if ($child.attr('cell-class')) {
                        $td.addClass($child.attr('cell-class'));
                    }
                    switch ($child[0].tagName.toLowerCase()) {
                        case 'separator':
                            break;
                        case 'label':
                            if ($child.attr('for')) {
                                $td.attr('width', '1%').addClass('oe_form_group_cell_label');
                                row_cols-= $td.attr('colspan') || 1;
                                total--;
                            }
                            break;
                        default:
                            var width = _.str.trim($child.attr('width') || ''),
                                iwidth = parseInt(width, 10);
                            if (iwidth) {
                                if (width.substr(-1) === '%') {
                                    total -= iwidth;
                                    width = iwidth + '%';
                                } else {
                                    // Absolute width
                                    $td.css('min-width', width + 'px');
                                }
                                $td.attr('width', width);
                                $child.removeAttr('width');
                                row_cols-= $td.attr('colspan') || 1;
                            } else {
                                to_compute.push($td);
                            }

                    }
                });
                if (row_cols) {
                    var unit = Math.floor(total / row_cols);
                    if (!$(this).is('.oe_form_group_row_incomplete')) {
                        _.each(to_compute, function($td, i) {
                            var width = parseInt($td.attr('colspan'), 10) * unit;
                            $td.attr('width', width + '%');
                            total -= width;
                        });
                    }
                }
            });
            _.each(children, function(el) {
                self.process($(el));
            });
            this.handle_common_properties($new_group, $group);
            return $new_group;
        },
        process_sheet: function($sheet) {
            var $new_sheet = this.render_element('FormRenderingSheet', $sheet.getAttributes());
            this.handle_common_properties($new_sheet, $sheet);
            var $dst = $new_sheet.find('.oe_form_sheet');
            $sheet.contents().appendTo($dst);
            $sheet.before($new_sheet).remove();
            $new_sheet.has('.oe_button_box').css({
                'padding-top': '50px',
            });
            this.process($new_sheet);
        },
        process_notebook: function ($notebook) {
            var self = this;
            var pages = [];
            $notebook.find('> page').each(function () {
                var $page = $(this);
                var page_attrs = $page.getAttributes();
                page_attrs.id = _.uniqueId('notebook_page_');
                var $new_page = self.render_element('FormRenderingNotebookPage', page_attrs);
                $page.contents().appendTo($new_page);
                $page.before($new_page).remove();
                var ic = self.handle_common_properties($new_page, $page).invisibility_changer;
                page_attrs.__page = $new_page;
                page_attrs.__ic = ic;
                pages.push(page_attrs);

                $new_page.children().each(function () {
                    self.process($(this));
                });
            });
            var $new_notebook = this.render_element('FormRenderingNotebook', {pages: pages});
            $notebook.contents().appendTo($new_notebook);
            $notebook.before($new_notebook).remove();
            self.process($($new_notebook.children()[0]));
            //tabs and invisibility handling
            $new_notebook.tabs();
            _.each(pages, function (page, i) {
                if (!page.__ic)
                    return;
                page.__ic.on("change:effective_invisible", null, function () {
                    if (!page.__ic.get('effective_invisible') && page.autofocus) {
                        $new_notebook.tabs('select', i);
                        return;
                    }
                    var current = $new_notebook.tabs("option", "selected");
                    if (!pages[current].__ic || !pages[current].__ic.get("effective_invisible"))
                        return;
                    var first_visible = _.find(_.range(pages.length), function (i2) {
                        return (!pages[i2].__ic) || (!pages[i2].__ic.get("effective_invisible"));
                    });
                    if (first_visible !== undefined) {
                        $new_notebook.tabs('select', first_visible);
                    }
                });
            });

            this.handle_common_properties($new_notebook, $notebook);
            // $new_notebook.before($('<div>').addClass('scroller scroller-left').css({'float': 'left'}).append($('<i>').addClass('fa fa-chevron-left'))
            //                                     .after($('<div>').addClass('scroller scroller-right').css({'float': 'left'}).append($('<i>').addClass('fa fa-chevron-right'))));
            return $new_notebook;
        },
        process_separator: function($separator) {
            var $new_separator = this.render_element('FormRenderingSeparator', $separator.getAttributes());
            $separator.before($new_separator).remove();
            this.handle_common_properties($new_separator, $separator);
            return $new_separator;
        },
        process_label: function($label) {
            var name = $label.attr("for"),
                field_orm = this.fvg.fields[name];
            var dict = {
                string: $label.attr('string') || (field_orm || {}).string || '',
                help: $label.attr('help') || (field_orm || {}).help || '',
                _for: name ? _.uniqueId('oe_field_input_') : undefined,
            };
            var $new_label = this.render_element('FormRenderingLabel', dict);
            $label.before($new_label).remove();
            this.handle_common_properties($new_label, $label);
            if (name) {
                this.labels[name] = $new_label;
            }
            return $new_label;
        },

    });

    instance.web.form.ResponsiveFieldEmail = instance.web.form.FieldEmail.extend({
        template: 'ResponsiveFieldEmail',
    });
    instance.web.form.ResponsiveFieldUrl = instance.web.form.FieldUrl.extend({
        template: 'ResponsiveFieldUrl',
    });

  	instance.web.form.ResponsiveFieldChar = instance.web.form.FieldChar.extend({
        template: 'ResponsiveFieldChar',
        widget_class: 'oe_form_field_char',
        events: {
            'change input': 'store_dom_value',
        },
        initialize_content: function () {
            this.setupFocus(this.$('input'));
        },
        store_dom_value: function () {
            if (!this.get('effective_readonly')
                    && this.$('input').length
                    && this.is_syntax_valid()) {
                this.internal_set_value(
                        this.parse_value(
                                this.$('input').val()));
            }
        },
        commit_value: function () {
            this.store_dom_value();
            return this._super();
        },
        render_value: function () {
            var show_value = this.format_value(this.get('value'), '');
            if (!this.get("effective_readonly")) {
                this.$el.find('input').val(show_value);
            } else {
                if (this.password) {
                    show_value = new Array(show_value.length + 1).join('*');
                }
                this.$(".oe_form_char_content").text(show_value);
            }
        },
        is_syntax_valid: function () {
            if (!this.get("effective_readonly") && this.$("input").size() > 0) {
                try {
                    this.parse_value(this.$('input').val(), '');
                    return true;
                } catch (e) {
                    return false;
                }
            }
            return true;
        },
        parse_value: function (val, def) {
            return instance.web.parse_value(val, this, def);
        },
        format_value: function (val, def) {
            return instance.web.format_value(val, this, def);
        },
        is_false: function () {
            return this.get('value') === '' || this._super();
        },
        focus: function () {
            var input = this.$('input:first')[0];
            return input ? input.focus() : false;
        },
        set_dimensions: function (height, width) {
            this._super(height, width);
            this.$('input').css({
                height: height,
                width: width
            });
        }
    });

    instance.web.form.ResponsiveFieldMany2One = instance.web.form.FieldMany2One.extend({
        template: "ResponsiveFieldMany2One",
    });

    instance.web.DateTimeWidget.include({
        template: "inshas.datepicker",
        jqueryui_object: 'datetimepicker',
        type_of_date: "datetime",
        pickTime: true,
        events: {
            // 'dp.change .input-group.date': 'change_datetime',
            // 'dp.change .input-group.date': 'on_picker_select',
            // 'dp.hide .input-group.date': 'on_picker_select',
            'change .oe_datepicker_master': 'change_datetime',
            'keypress .oe_datepicker_master': 'change_datetime',
        },
        start: function () {
            var self = this;
            this.$input = this.$el.find('.oe_datepicker_master');
            this.$input_picker = this.$el.find('.input-group.date');
            moment.locale(Date.CultureInfo.name, {
              week: {
                dow: Date.CultureInfo.firstDayOfWeek,
              }
            });

            var format_ = this.pickTime ? "L HH:mm:ss" : "L"

            this.picker({
                defaultDate: Date.now(),
                toolbarPlacement: 'bottom',
                showTodayButton: true,
                showClear: true,
                showClose: false,
                format: format_,
                calendarWeeks: true,
                useCurrent: true
            });

            this.set_readonly(false);
            this.set({'value': false});
            this.$input_picker.on('dp.hide', function(ev){
                self.on_picker_close(ev.date.format(self.pickTime ? "L HH:mm:ss" : "L"), ev.date);
                self.change_datetime(ev);
            });
            this.$input_picker.on('dp.change', function(ev){
                self.on_picker_select(ev.date.format(self.pickTime ? "L HH:mm:ss" : "L"), ev.date);
                self.change_datetime(ev);
            });
        },
        picker: function() {
            if (this.jqueryui_object !== 'datetimepicker'){
                this.jqueryui_object = 'datetimepicker';
            }
            return $.fn[this.jqueryui_object].apply(this.$input_picker, arguments);
        },
        on_picker_close: function (text, date_) {
            this.on_picker_select(text, date_);
            this.$input.focus();
        },
        on_picker_select: function(text, date_) {
            var date = date_;
            this.$input
                .val(date ? this.format_client(date._d) : '');
            this.$input.trigger('change');
        },
        set_value: function(value_) {
            this.set({'value': value_});
            this.$input.val(value_ ? this.format_client(value_) : '');
        },
        get_value: function() {
            return this.get('value');
        },
        set_value_from_ui_: function() {
            var value_ = this.$input.val() || false;
            this.set({'value': this.parse_client(value_)});
        },
        set_readonly: function(readonly) {
            this.readonly = readonly;
            this.$input.prop('readonly', this.readonly);
            this.$el.find('img.oe_datepicker_trigger').toggleClass('oe_input_icon_disabled', readonly);
        },
        is_valid_: function() {
            var value_ = this.$input.val();
            if (value_ === "") {
                return true;
            } else {
                try {
                    this.parse_client(value_);
                    return true;
                } catch(e) {
                    return false;
                }
            }
        },
        parse_client: function(v) {
            return instance.web.parse_value(v, {"widget": this.type_of_date});
        },
        format_client: function(v) {
            return instance.web.format_value(v, {"widget": this.type_of_date});
        },
        change_datetime: function(e) {
            if ((e.type !== "keypress" || e.which === 13) && this.is_valid_()) {
                this.set_value_from_ui_();
                this.trigger("datetime_changed");
            }
        },
        commit_value: function () {
            this.change_datetime();
        },
    });

    instance.web.ResponsiveDateWidget = instance.web.DateTimeWidget.extend({
        jqueryui_object: 'datetimepicker',
        type_of_date: "date",
        pickTime: false,

    });

    instance.web.form.ResponsiveFieldDatetime = instance.web.form.FieldDatetime.extend({
        build_widget: function () {
            return new instance.web.DateTimeWidget(this);
        },
    });

    instance.web.form.ResponsiveFieldDate = instance.web.form.FieldDate.extend({
        build_widget: function () {
            return new instance.web.ResponsiveDateWidget(this);
        }
    });

    instance.web.form.One2ManyListView.include({
        _template: 'ResponsiveOne2Many.listview',
    });

    instance.web.form.ResponsiveFieldFloat = instance.web.form.ResponsiveFieldChar.extend({
        is_field_number: true,
        widget_class: 'oe_form_field_float',
        init: function (field_manager, node) {
            this._super(field_manager, node);
            this.internal_set_value(0);
            if (this.node.attrs.digits) {
                this.digits = this.node.attrs.digits;
            } else {
                this.digits = this.field.digits;
            }
        },
        set_value: function (value_) {
            if (value_ === false || value_ === undefined) {
                // As in GTK client, floats default to 0
                value_ = 0;
            }
            if (this.digits !== undefined && this.digits.length === 2) {
                value_ = instance.web.round_decimals(value_, this.digits[1]);
            }
            this._super.apply(this, [value_]);
        },
        focus: function () {
            var $input = this.$('input:first');
            return $input.length ? $input.select() : false;
        }
    });

    instance.web.form.ResponsiveFieldText = instance.web.form.FieldText.extend({
        template: 'ResponsiveFieldText',
    });

    instance.web.form.ResponsiveFieldMany2ManyTags = instance.web.form.FieldMany2ManyTags.extend({
        template: "ResponsiveFieldMany2ManyTags",
    });
    instance.web.form.ResponsiveFieldSelection = instance.web.form.FieldSelection.extend({
        template: 'ResponsiveFieldSelection',
        render_value: function () {
            var values = this.get("values");
            values = [[false, this.node.attrs.placeholder || '']].concat(values);
            var found = _.find(values, function (el) {
                return el[0] === this.get("value");
            }, this);
            if (!found) {
                found = [this.get("value"), _t('Unknown')];
                values = [found].concat(values);
            }
            if (!this.get("effective_readonly")) {
                this.$().html(QWeb.render("ResponsiveFieldSelectionSelect", {widget: this, values: values}));
                this.$("select").val(JSON.stringify(found[0]));
            } else {
                this.$el.text(found[1]);
            }
        },
    });
    instance.web.form.ResponsiveFieldBoolean = instance.web.form.FieldBoolean.extend({
        template: 'ResponsiveFieldBoolean',
    });
    instance.web.form.ResponsiveFieldRadio = instance.web.form.FieldRadio.extend({
        template: 'ResponsiveFieldRadio',
    });
    // instance.web.form.original_widgets = instance.web.form.widgets.extend({});
    instance.web.form.widgets = instance.web.form.widgets.extend({
        'char': 'instance.web.form.ResponsiveFieldChar',
        'email': 'instance.web.form.ResponsiveFieldEmail',
        'url': 'instance.web.form.ResponsiveFieldUrl',
        'date': 'instance.web.form.ResponsiveFieldDate',
        'datetime': 'instance.web.form.ResponsiveFieldDatetime',
        'many2one': 'instance.web.form.ResponsiveFieldMany2One',
        'float': 'instance.web.form.ResponsiveFieldFloat',
        'integer': 'instance.web.form.ResponsiveFieldFloat',
        'float_time': 'instance.web.form.ResponsiveFieldFloat',
        'text': 'instance.web.form.ResponsiveFieldText',
        'many2many_tags': 'instance.web.form.ResponsiveFieldMany2ManyTags',
        'image': 'instance.web.form.FieldBinaryImage',
        'selection': 'instance.web.form.ResponsiveFieldSelection',
        'boolean': 'instance.web.form.ResponsiveFieldBoolean',
        'radio': 'instance.web.form.ResponsiveFieldRadio',


        'many2many': 'instance.web.form.FieldMany2Many',
        'one2many': 'instance.web.form.FieldOne2Many',
        'one2many_list': 'instance.web.form.FieldOne2Many',

        'html': 'instance.web.form.FieldTextHtml',

        'id': 'instance.web.form.FieldID',
        'char_domain': 'instance.web.form.FieldCharDomain',
        'many2onebutton': 'instance.web.form.Many2OneButton',
        'many2many_kanban': 'instance.web.form.FieldMany2ManyKanban',
        'reference': 'instance.web.form.FieldReference',
        'percentpie': 'instance.web.form.FieldPercentPie',
        'barchart': 'instance.web.form.FieldBarChart',
        'progressbar': 'instance.web.form.FieldProgressBar',
        'binary': 'instance.web.form.FieldBinaryFile',
        'many2many_binary': 'instance.web.form.FieldMany2ManyBinaryMultiFiles',
        'statusbar': 'instance.web.form.FieldStatus',
        'monetary': 'instance.web.form.FieldMonetary',
        'many2many_checkboxes': 'instance.web.form.FieldMany2ManyCheckBoxes',
        'x2many_counter': 'instance.web.form.X2ManyCounter',
        'priority': 'instance.web.form.Priority',
        'kanban_state_selection': 'instance.web.form.KanbanSelection',
        'statinfo': 'instance.web.form.StatInfo',
    });
})();

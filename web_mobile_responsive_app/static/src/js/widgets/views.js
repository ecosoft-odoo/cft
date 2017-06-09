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

    instance.web.View.include({
        load_view: function (context) {
            var self = this;
            var view_loaded_def;
            if (this.embedded_view) {
                view_loaded_def = $.Deferred();
                $.async_when().done(function () {
                    view_loaded_def.resolve(self.embedded_view);
                });
            } else {
                if (!this.view_type)
                    console.warn("view_type is not defined", this);
                view_loaded_def = instance.web.fields_view_get({
                    "model": this.dataset._model,
                    "view_id": this.view_id,
                    "view_type": this.view_type,
                    "toolbar": !!this.options.$sidebar,
                    "context": this.dataset.get_context(),
                });
            }
            return this.alive(view_loaded_def).then(function (r) {
                self.fields_view = r;
                // add css classes that reflect the (absence of) access rights
                self.$el.addClass('oe_view')
                        .toggleClass('oe_cannot_create', !self.is_action_enabled('create'))
                        .toggleClass('oe_cannot_edit', !self.is_action_enabled('edit'))
                        .toggleClass('oe_cannot_delete', !self.is_action_enabled('delete'));
                return $.when(self.view_loading(r)).then(function () {
                    self.trigger('view_loaded', r);
                    window.on_scroll_fix_tools();
                });
            });
        },
    });

    instance.web.Loading.include({
        template: _t("Loading"),
        init: function(parent) {
            this._super(parent);
            this.count = 0;
            this.blocked_ui = false;
            this.session.on("request", this, this.request_call);
            this.session.on("response", this, this.response_call);
            this.session.on("response_failed", this, this.response_call);
        },
        destroy: function() {
            this.on_rpc_event(-this.count);
            this._super();
        },
        request_call: function() {
            this.on_rpc_event(1);
        },
        response_call: function() {
            this.on_rpc_event(-1);
        },
        on_rpc_event : function(increment) {
            var self = this;
            if (!this.count && increment === 1) {
                // Block UI after 3s
                this.long_running_timer = setTimeout(function () {
                    self.blocked_ui = true;
                    instance.web.blockUI();
                }, 3000);
            }

            this.count += increment;
            if (this.count > 0) {
                if (instance.session.debug) {
                    this.$el.text(_.str.sprintf( _t("Loading (%d)"), this.count));
                } else {
                    this.$el.text(_t("Loading"));
                }
                this.$el.show();
                this.getParent().$el.addClass('oe_wait');
            } else {
                this.count = 0;
                clearTimeout(this.long_running_timer);
                // Don't unblock if blocked by somebody else
                if (self.blocked_ui) {
                    this.blocked_ui = false;
                    instance.web.unblockUI();
                }
                this.$el.fadeOut();
                this.getParent().$el.removeClass('oe_wait');
            }
        }
    });

    instance.web.ViewManagerAction.include({
        template: "ResponsiveViewManagerAction",
    });
    instance.web.ActionManager.include({

        on_breadcrumb_clicked: function (ev) {
            var $e = $(ev.target);
            var id = $e.data('id');
            var index;
            for (var i = this.breadcrumbs.length - 1; i >= 0; i--) {
                if (this.breadcrumbs[i].id == id) {
                    index = i;
                    break;
                }
            }
            var subindex = $e.parent().find('a.oe_breadcrumb_item[data-id=' + $e.data('id') + ']').index($e);
            this.select_breadcrumb(index, subindex);
            window.on_scroll_fix_tools();
        },
    });

    instance.web.ViewManager.include({
        start: function () {
            // this._super.apply(this, arguments);
            var self = this;
            this.$el.find('.oe_view_manager_switch a').click(function () {
                self.switch_mode($(this).data('view-type'));
            }).tooltip();
            var views_ids = {};
            _.each(this.views_src, function (view) {
                self.views[view.view_type] = $.extend({}, view, {
                    deferred: $.Deferred(),
                    controller: null,
                    options: _.extend({
                        $buttons: self.$el.find('.oe_view_manager_buttons'),
                        $sidebar: self.flags.sidebar ? self.$el.find('.oe_view_manager_sidebar') : undefined,
                        $pager: self.$el.find('.oe_view_manager_pager'),
                        action: self.action,
                        action_views_ids: views_ids
                    }, self.flags, self.flags[view.view_type] || {}, view.options || {})
                });

                views_ids[view.view_type] = view.view_id;
            });
            if (this.flags.views_switcher === false) {
                this.$el.find('.oe_view_manager_switch').hide();
            }
            this.$el.find('sidebar-small, pager-small').click(function(e) {
                e.stopPropagation();
                $('sidebar-small .dropdown-toggle').dropdown();
            });
            $(window).on('resize', self.reposition_sidebar_and_pager);
            self.reposition_sidebar_and_pager();
            // If no default view defined, switch to the first one in sequence
            var default_view = this.flags.default_view || this.views_src[0].view_type;

            return this.switch_mode(default_view, null, this.flags[default_view] && this.flags[default_view].options);
        },
        reposition_sidebar_and_pager: function(){
            var $el = $('div.oe_view_manager');
            var is_large = $('.more_options').is(':hidden');
            if (is_large) {
                $el.find('pager-large').append($el.find('pager-small .oe_view_manager_pager'));
                $el.find('sidebar-large').append($el.find('sidebar-small .oe_view_manager_sidebar'));
            } else {
                $el.find('pager-small').append($el.find('pager-large .oe_view_manager_pager'));
                $el.find('sidebar-small').append($el.find('sidebar-large .oe_view_manager_sidebar'));
            }

        },
    });


})()
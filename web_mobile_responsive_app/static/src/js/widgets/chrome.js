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
    instance.web.Menu.include({
        bind_menu: function() {
            var self = this;
            this.$secondary_menus = this.$el.parents().find('.oe_secondary_menus_container')
            this.$secondary_menus.on('click', 'a[data-menu]', this.on_menu_click);
            this.$el.on('click', 'a[data-menu]', this.on_top_menu_click);
            $('#MoreAppsModal').on('click', 'a[data-menu]', function(e){
                var $target = $(e.target);
                self.on_top_menu_click(e);
                $('#MoreAppsModal').modal('hide');
                $('#MoreAppsModal').find('.active').removeClass('active');
                $target.closest('li').addClass('active');

            });

            // Hide second level submenus
            this.$secondary_menus.find('.oe_menu_toggler').siblings('.oe_secondary_submenu').hide();
            if (self.current_menu) {
                self.open_menu(self.current_menu);
            }
            this.trigger('menu_bound');

            var lazyreflow = _.debounce(this.reflow.bind(this), 200);
            instance.web.bus.on('resize', this, function() {
                if (parseInt(self.$el.parent().css('width')) <= 768 ) {
                    lazyreflow('all_inside');
                } else {
                    lazyreflow();
                }
            });
            instance.web.bus.trigger('resize');

            this.is_bound.resolve();
        },
        open_menu: function (id) {
            this.current_menu = id;
            this.session.active_id = id;
            var $clicked_menu, $sub_menu, $main_menu;
            $clicked_menu = this.$el.add(this.$secondary_menus).find('a[data-menu=' + id + ']');
            this.trigger('open_menu', id, $clicked_menu);

            if (this.$secondary_menus.has($clicked_menu).length) {
                $sub_menu = $clicked_menu.parents('.oe_secondary_menu');
                $main_menu = this.$el.find('a[data-menu=' + $sub_menu.data('menu-parent') + ']');
            } else {
                $sub_menu = this.$secondary_menus.find('.oe_secondary_menu[data-menu-parent=' + $clicked_menu.attr('data-menu') + ']');
                $main_menu = $clicked_menu;
            }

            // Activate current main menu
            this.$el.find('.active').removeClass('active');

            $main_menu.parent().addClass('active');
            $main_menu.parents('li.has-submenu').addClass('active');

            // Show current sub menu
            this.$secondary_menus.find('.oe_secondary_menu').hide();
            $sub_menu.show();

            // Hide/Show the leftbar menu depending of the presence of sub-items
            this.$secondary_menus.parent('.oe_leftbar').toggle(!!$sub_menu.children().length);

            // Activate current menu item and show parents
            this.$secondary_menus.find('.active').removeClass('active');
            if ($main_menu !== $clicked_menu) {
                // $clicked_menu.parents().show();
                if ($clicked_menu.is('.oe_menu_toggler')) {
                    // Close the menus at the same level when on of them is opened.
                    $clicked_menu.parents('li').siblings('li').find('>.oe_menu_toggler')
                    .removeClass('oe_menu_opened').siblings('.oe_secondary_submenu').hide();
                    $clicked_menu.toggleClass('oe_menu_opened').siblings('.oe_secondary_submenu:first').toggle();
                } else {
                    $clicked_menu.parent().addClass('active');
                    $clicked_menu.closest('li.has-submenu').addClass('active');
                }
            }

            // add a tooltip to cropped menu items
            this.$secondary_menus.find('.oe_secondary_submenu li a span').each(function() {
                $(this).tooltip(this.scrollWidth > this.clientWidth ? {title: $(this).text().trim(), placement: 'right'} :'destroy');
           });
        },

        reflow: function(behavior) {
            var self = this;
            var $more_container = this.$('#menu_more_container').hide();
            var $more = this.$('#menu_more');
            var $systray = this.$el.parents().find('.oe_systray');

            $more.children('li').insertBefore($more_container);  // Pull all the items out of the more menu

            // 'all_outside' beahavior should display all the items, so hide the more menu and exit
            if (behavior === 'all_outside') {
                this.$el.find('li').show();
                $more_container.hide();
                return;
            }

            var $toplevel_items = this.$el.find('li').not($more_container).not($systray.find('li')).hide();
            $toplevel_items.each(function() {
                // In all inside mode, we do not compute to know if we must hide the items, we hide them all
                if (behavior === 'all_inside') {
                    return false;
                }
                var remaining_space = self.$el.parent().width() - $more_container.outerWidth() - 100;
                self.$el.parent().children(':visible').each(function() {
                    remaining_space -= $(this).outerWidth();
                });

                if ($(this).width() > remaining_space) {
                    return false;
                }
                $(this).show();
            });
            $more.append($toplevel_items.filter(':hidden').show());
            $more_container.toggle(!!$more.children().length || behavior === 'all_inside');
            // Hide toplevel item if there is only one
            var $toplevel = this.$el.children("li:visible");
            if ($toplevel.length === 1 && behavior != 'all_inside') {
                $toplevel.hide();
            }
        },
    });
})();

/* © 2016 ACSONE SA/NV (<http://acsone.eu>)
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */
openerp.date_range = function(instance) {
"use strict";

    var _t = instance.web._t;
    var _lt = instance.web._lt;

    instance.web.search.ExtendedSearchProposition.include({
        select_field: function(field) {
            this._super.apply(this, arguments);
            this.field = field;
            this.type = field.type
            this.is_date_range_selected = false;
            this.is_date = this.type == 'date' || this.type == 'datetime';
            this.$value = this.$el.find('.searchview_extended_prop_value');
            if (this.is_date) {
                var ds = new instance.web.DataSetSearch(this, 'date.range.type', this.context, [[1, '=', 1]]);
                ds.read_slice(['name'], {}).done(this.proxy('add_date_range_types_operator'));
            }
        },

        add_date_range_types_operator: function(date_range_types) {
            var self = this;
            _.each(date_range_types, function(drt) {
                $('<option>', {value: 'drt_' + drt.id})
                    .text(drt.name)
                    .appendTo(self.$el.find('.searchview_extended_prop_op'));
            });
        },

        operator_changed: function (e) {
            var val = $(e.target).val();
            this.is_date_range_selected = val.startsWith('drt_');
            if (this.is_date_range_selected) {
                var type_id = val.replace('drt_', '');
                this.date_range_type_operator_selected(type_id);
                return;
            }
            if (this.is_date) {
                this.on_date_type_selected(this.type, this.field);
            }
            this._super.apply(this, arguments);
        },

        date_range_type_operator_selected: function(type_id) {
            this.$value.empty().show();
            var ds = new instance.web.DataSetSearch(this, 'date.range', this.context, [['type_id', '=', parseInt(type_id)]]);
            ds.read_slice(['name','date_start', 'date_end'], {}).done(this.proxy('on_range_type_selected'));
        },

        on_range_type_selected: function(date_range_values) {
            this.value = new instance.web.search.ExtendedSearchProposition.DateRange(this, this.value.field, date_range_values);
            this.value.appendTo(this.$value);
            this.value.on_range_selected();
        },

        on_date_type_selected: function(type, field) {
            this.$value.empty().show();
            var Field = instance.web.search.custom_filters.get_object(type);
            this.value = new Field(this, field);
            this.value.appendTo(this.$value)
        },

        get_proposition: function () {
            var res = this._super.apply(this, arguments);
            if (this.is_date_range_selected) {
                // in case of date.range, the domain is provided by the server and we don't
                // want to put nest the returned value into an array.
                res.value = this.value.domain
            }
            return res;
        },
    });

    instance.web.search.ExtendedSearchProposition.DateRange = instance.web.search.ExtendedSearchProposition.Field.extend({
        template: 'SearchView.extended_search.dateRange.selection',
        events: {
            'change': 'on_range_selected',
        },

        init: function (parent, field, date_range_values) {
            this._super(parent, field);
            this.date_range_values = date_range_values;
        },

        toString: function () {
            var select = this.$el[0];
            var option = select.options[select.selectedIndex];
            var res = "";
            if (typeof option != 'undefined') {
                res = option.label || option.text;
            }
            return res;
        },

        get_value: function() {
            return parseInt(this.$el.val());
        },

        on_range_selected: function(e) {
            var self = this;
            self.domain = '';
            instance.web.blockUI();
            new instance.web.Model("date.range")
                .call("get_domain",  [
                    [this.get_value()],
                    this.field.name,
                    {}
                ])
                .then(function (domain) {
                    instance.web.unblockUI();
                    self.domain = domain;
                });
        },

        get_domain: function (field, operator) {
            return this.domain;
        },
    });

    instance.web.search.Advanced.include({
        commit_search: function () {
            if (! $('.searchview_extended_prop_op').val().startsWith('drt_')) {
                this._super.apply(this, arguments);
            } else {
                // Get domain sections from all propositions
                var children = this.getChildren();
                var propositions = _.invoke(children, 'get_proposition');
                var domain = propositions[0].value;
                this.view.query.add({
                    category: _t("Advanced"),
                    values: propositions,
                    field: {
                        get_context: function () { },
                        get_domain: function () { return domain;},
                        get_groupby: function () { }
                    }
                });

                // remove all propositions
                _.invoke(children, 'destroy');
                // add new empty proposition
                this.append_proposition();
                // TODO: API on searchview
                this.view.$el.removeClass('oe_searchview_open_drawer');
            }
        }
    })

    instance.web.SearchView.include({
        build_search_data: function () {
            var res = this._super.apply(this, arguments);
            if ($('.searchview_extended_prop_op').val() != undefined && $('.searchview_extended_prop_op').val().startsWith('drt_')) {
                var domains = [];
                this.query.each(function (facet) {
                    var field = facet.get('field');
                    try {
                        var domain = field.get_domain(facet);
                        if (Array.isArray(domain) && domain.length == 2) {
                            for (var i = 0; i < domain.length; i++) {
                                domains.push(domain[i]);
                            }
                        } else {
                            domains.push(domain);
                        }
                    } catch (e) {
                        if (e instanceof instance.web.search.Invalid) {
                            res.errors.push(e);
                        } else {
                            throw e;
                        }
                    }
                })
            }
            return res;
        }
    })
};

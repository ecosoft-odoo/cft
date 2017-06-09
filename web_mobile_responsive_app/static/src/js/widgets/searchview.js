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

var isMobile = function(){
  var isMob = false; //initiate as false
  // device detection
  if(/(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|ipad|iris|kindle|Android|Silk|lge |maemo|midp|mmp|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows (ce|phone)|xda|xiino/i.test(navigator.userAgent)
      || /1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(navigator.userAgent.substr(0,4))){
      isMob = true;
    }
    return isMob;
}

instance.web.SearchView.include({
  /**
   * @param {openerp.web.search.SearchQuery | undefined} Undefined if event is change
   * @param {openerp.web.search.Facet}
   * @param {Object} [options]
   */
  renderFacets: function (collection, model, options) {
      var self = this;
      var started = [];
      var $e = this.$('div.oe_searchview_facets');
      _.invoke(this.input_subviews, 'destroy');
      this.input_subviews = [];

      var i = new instance.web.search.InputView(this);
      started.push(i.appendTo($e));
      this.input_subviews.push(i);
      this.query.each(function (facet) {
          var f = new instance.web.search.FacetView(this, facet);
          started.push(f.appendTo($e));
          self.input_subviews.push(f);

          var i = new instance.web.search.InputView(this);
          started.push(i.appendTo($e));
          self.input_subviews.push(i);
      }, this);
      _.each(this.input_subviews, function (childView) {
          childView.on('focused', self, self.proxy('childFocused'));
          childView.on('blurred', self, self.proxy('childBlurred'));
      });

      $.when.apply(null, started).then(function () {
          if (options && options.focus_input === false) return;
          var input_to_focus;
          // options.at: facet inserted at given index, focus next input
          // otherwise just focus last input
          if (!options || typeof options.at !== 'number') {
              input_to_focus = _.last(self.input_subviews);
          } else {
              input_to_focus = self.input_subviews[(options.at + 1) * 2];
          }
          if (!isMobile()){
            input_to_focus.$el.focus();
          }
      });
  }
});

instance.web.search.FacetView.include({
	events: {
        'focus': function () { this.trigger('focused', this); },
        'blur': function () { this.trigger('blurred', this); },
        'click': function (e) {
            if ($(e.target).is('.oe_facet_remove>.fa.fa-times')) {
                this.model.destroy();
                return false;
            }
            this.$el.focus();
            e.stopPropagation();
        },
        'keydown': function (e) {
            var keys = $.ui.keyCode;
            switch (e.which) {
            case keys.BACKSPACE:
            case keys.DELETE:
                this.model.destroy();
                return false;
            }
        }
    },
});

instance.web.search.CustomFilters.include({
	facet_for: function (filter) {
        return {
            category: _t("Custom Filter"),
            field: {
                get_context: function () { return filter.context; },
                get_groupby: function () { return [filter.context]; },
                get_domain: function () { return filter.domain; }
            },
            _id: filter['id'],
            is_custom_filter: true,
            values: [{label: filter.name, value: null}]
        };
    },
});

instance.web.search.Filters = instance.web.search.Input.extend({
    template: 'SearchView.Filters',
    _in_drawer: true,
    start: function () {
        var self = this;
        var is_group = function (i) { return i instanceof instance.web.search.FilterGroup; };
        var visible_filters = _(this.drawer.controls).chain().reject(function (group) {
            return _(_(group.children).filter(is_group)).isEmpty()
                || group.modifiers.invisible;
        });

        var groups = visible_filters.map(function (group) {
                var filters = _(group.children).filter(is_group);
                return {
                    name: _.str.sprintf("<span class='oe_i'>%s</span> %s",
                            group.icon, group.name),
                    filters: filters,
                    length: _(filters).chain().map(function (i) {
                        return i.filters.length; }).sum().value()
                };
            }).value();

        var $dl = $('<dl class="dl-horizontal">').appendTo(this.$el);

        var rendered_lines = _.map(groups, function (group) {
            $('<dt>').html(group.name).appendTo($dl);
            var $dd = $('<dd>').appendTo($dl);
            return $.when.apply(null, _(group.filters).invoke('appendTo', $dd));
        });

        return $.when.apply(this, rendered_lines);
    },
});

})()

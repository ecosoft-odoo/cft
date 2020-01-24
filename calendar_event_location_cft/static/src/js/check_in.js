openerp.calendar_event_location_cft = function (instance) {
    var QWeb = instance.web.qweb;
    var _t = instance.web._t;
    var _lt = instance.web._lt;

    getLocation();

    function getLocation() {
        if (navigator.geolocation) {
            var address = navigator.geolocation.getCurrentPosition(showPosition);
        } else {
            alert("Geolocation is not supported by this browser.");
        }
    }
    function showPosition(position) {
        var latitude = position.coords.latitude;
        var longitude = position.coords.longitude;
        var geocoder = new google.maps.Geocoder();
        var latLng   = new google.maps.LatLng(
            position.coords.latitude, position.coords.longitude);
        geocoder.geocode({'latLng': latLng}, function(results, status) {
            if (status == 'OK') {
              return results[0]['format_address'];
            } else {
              alert('Geocode was not successful for the following reason: ' + status);
            }
        });
    }

    instance.calendar_event_location_cft.check_in = instance.web.FormView.extend({
        // template: 'calendar.event',
        // init: function (parent) {
        //     this._super(parent);
        // },
        // events: {
        //     'click .location_check_in': 'do_check_in',
        // },
        start: function() {
            var self = this;
            this.$(".location_check_in").click(function(ev) {
                ev.preventDefault();
                self.do_check_in();
            });
        },
        do_check_in: function () {
            alert('Hello!!!');
            var self = this;
            var calendar_event = new instance.web.DataSet(self, 'calendar.event');
            // calendar_event.call('button_check_in', []).done(function (result) {
            //     self.last_sign = new Date();
            //     self.set({"signed_in": ! self.get("signed_in")});
            // });
        },
    });

    // instance.web.UserMenu.include({
    //     do_update: function () {
    //         this._super();
    //         var self = this;
    //         this.update_promise.done(function () {
    //             if (!_.isUndefined(self.attendanceslider)) {
    //                 return;
    //             }
    //             // check current user is an employee
    //             var Users = new instance.web.Model('res.users');
    //             Users.call('has_group', ['base.group_user']).done(function(is_employee) {
    //                 if (is_employee) {
    //                     self.attendanceslider = new instance.hr_attendance.AttendanceSlider(self);
    //                     self.attendanceslider.prependTo(instance.webclient.$('.oe_systray'));
    //                 } else {
    //                     self.attendanceslider = null;
    //                 }
    //             });
    //         });
    //     },
    // });
};

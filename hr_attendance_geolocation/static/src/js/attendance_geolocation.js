openerp.hr_attendance_geolocation = function (instance) {
    'use strict';

    instance.hr_attendance.AttendanceSlider.include({
        init: function () {
            this._super.apply(this, arguments);
            this.location = (null, null);
            this.errorCode = null;
        },
        do_update_attendance: function () {
            var self = this;
            var options = {
                enableHighAccuracy: true,
                timeout: 5000,
                maximumAge: 0,
            };
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    self._manual_attendance.bind(self), self._getPositionError,
                    options);
            }
        },
        _manual_attendance: function (position) {
            var self = this;
            openerp.jsonRpc('/web/dataset/call', 'call', {
                model: 'hr.employee',
                method: 'attendance_action_change',
                args: [[self.employee.id],
                    {'attendance_location': [position.coords.latitude,
                        position.coords.longitude]}],
            }).then(function (result) {
                if (result.action) {
                    self.do_action(result.action);
                } else if (result.warning) {
                    self.do_warn(result.warning);
                }
            });
        },
        _getPositionError: function () {
            console.warn('ERROR(${error.code}): ${error.message}');
        },
    });
};

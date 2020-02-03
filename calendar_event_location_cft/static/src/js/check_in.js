openerp.calendar_event_location_cft = function (instance) {

    var QWeb = instance.web.qweb;
    var _t = instance.web._t;
    var _lt = instance.web._lt;

    instance.web.form.WidgetButton.include({
        on_click: function() {
            var self = this;
            if (self.node.attrs.name == "button_check_in") {
                if (navigator.geolocation) {
                    var options = {
                        enableHighAccuracy: true,
                        timeout: 5000,
                        maximumAge: 0,
                    };
                    navigator.geolocation.getCurrentPosition(
                        self.getCurrentLocation.bind(self),
                        self.getLocationError, options);
                } else {
                    alert("Geolocation is not supported by this browser.");
                }
            }
            this._super();
        },
        getCurrentLocation: function(position) {
            self = this;
            var latitude = position.coords.latitude;
            var longitude = position.coords.longitude;
            var geocoder = new google.maps.Geocoder();
            var latLng = new google.maps.LatLng(latitude, longitude);
            geocoder.geocode({'latLng': latLng}, function (results, status) {
                if (status == google.maps.GeocoderStatus.OK) {
                    var model = new openerp.Model('calendar.event');
                    var record_id = self.field_manager.datarecord.id;
                    var location = results[0].formatted_address;
                    model.call('write', [record_id, {
                            'latitude': latitude,
                            'longitude': longitude,
                            'location': location}]).then(function(result) {
                        alert("Save location success.");
                        self.do_action('reload');
                    });
                } else {
                    alert("Geocode was not successful for the following reason: " + status);
                }
            });
        },
        getLocationError: function (error) {
            console.warn(error.message);
        },
    })
}

openerp.single_login = function (instance){
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

setInterval(updateExpiry,60*1000);

function getCookie(key) {
    var keyValue = document.cookie.match('(^|;) ?' + key + '=([^;]*)(;|$)');
    return keyValue ? keyValue[2] : null;
};

function updateExpiry() {
    // one heartbeat per browser, not per tab
    var now = Date.now(), last = 0;
    try { last = parseInt(localStorage.getItem('single_login_ping') || '0', 10); } catch (e) {}
    if (now - last < 50*1000) { return; }
    try { localStorage.setItem('single_login_ping', String(now)); } catch (e) {}
    new instance.web.Model("res.users").call("save_session").done(function(data) {return data});
};


instance.web.WebClient.include({
    on_logout: function() {
        var self = this;
        if (!this.has_uncommitted_changes()) {
            //call res.users to clear user session.
            new instance.web.Model("res.users").call("clear_session").done(function(data) {return data});
            
            self.action_manager.do_action('logout');
        }
    },
});

};
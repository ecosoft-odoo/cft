(function(){
    var instance = openerp;
    var QWeb = instance.web.qweb,
          _t =  instance.web._t,
          _lt = instance.web._lt;

  openerp.session.rpc('/web/session/modules', {}).then(function(result){
    if(_.indexOf(result, 'mail') !== -1){
      instance.mail_followers.Followers.include({
        template: 'mail.followers_responsive',
      });
    }


  })
})()

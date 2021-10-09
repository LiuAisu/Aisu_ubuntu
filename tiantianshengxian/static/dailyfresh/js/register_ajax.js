$(function(){
            $('#btnLogin').click(function(){
                // 1. 获取用户名和密码
                username = $('#user_name').val()
                password = $('#pwd').val()
                email = $('#email').val()
                // 2. 发起post ajax请求 /login_ajax_cheak，携带用户名和密码
                $.ajax({
                    'url':'/user/regiter_ajax_handle/',
                    'type':'post',
                    'data':{'username':username, 'password':password, 'email':email},
                    'dataType':'json',
                }).success(function (data) {
                    // 登录成功 返回{'res':1}
                    // 登录失败 返回{'res':0}
                    if(data.res == 1){
                        location.href = '/index/'
                    }
                })
            })
        })
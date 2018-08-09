function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(function () {

    $(".pass_info").submit(function (e) {
        e.preventDefault();

        var old_password = $("#old_password").val();
        var new_password = $("#new_password").val();
        var new_que_password = $("#new_que_password").val();

             $.post('/user/password',{
              'old_password':old_password,
              'new_password':new_password,
             'new_que_password':new_que_password,
             'csrf_token':$('#csrf_token').val()
    },function (data) {
         if (data.result == 5) {
             $('.input_txt').html(new_password);
             alert('修改密码成功');
         }
         else if (data.result == 2) {
             alert('请把数据填写完整');
         } else if (data.result == 3) {
             alert('密码不一致');
         } else if (data.result == 4) {
             alert('密码格式不对');
         } else if (data.result == 1) {
             alert('旧密码不对');
         }
     })


    });
})







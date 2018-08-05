function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(function () {

    $(".base_info").submit(function (e) {
        e.preventDefault()

        var signature = $("#signature").val();
        var nick_name = $("#nick_name").val();
        var gender = $(".gender:checked").val();

        if (!nick_name) {
            alert('请输入昵称')
            return
        }
        if (!gender) {
            alert('请选择性别')
        }

        // TODO 修改用户信息接口
        $.post('/user/base',{
            'signature':signature,
            'nick_name':nick_name,
             'gender':gender,
             'csrf_token':$('#csrf_token').val()
        },function (data) {
            if(data.result==2){
                //成功
                //左侧修改
                //第一个参数表示要找的东西，第二个参数表示范围，父窗口
                //window 表示当前窗口，
                //parent 表示父窗口，当前使用了iframe进行了窗口嵌套
                //document表示某个窗口的所有html元素
                $('.user_center_name',window.parent.document).html(nick_name);
                //右侧修改
                $('#nick_name',window.parent.document).html(nick_name);
            }
            })

    });
})
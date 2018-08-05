function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(function () {
    $('.pic_info').submit(function (e) {
        e.preventDefault();
        //$.post()://这个方法不能提交文件
        //$(this)表示表单对象
        //ajaxSumbit()方法由jquery.form.min.js提供
        $(this).ajaxSubmit({
            url:"/user/pic",
            type:"post",
            dataType:"json",
            success:function (data) {

                //更新当前页面
                $('.now_user_pic').attr("src",data.avatar);
                //更新左侧头像
                $('.user_center_pic img',window.parent.document).attr('src',data.avatar);

                //g更新右上角头像
                $('.lgin_pic',window.parent.document).attr('src',data.avatar);
            }
        });
    });
})
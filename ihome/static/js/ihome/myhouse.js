function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(document).ready(function(){
    // 查询用户的实名认证信息
    $.get("/api_1_0/user/auth", function (resp) {
        // 4101代表用户未登录
        if ("4101" == resp.errno) {
            location.href = "/login.html";
        } else if ("0" == resp.errno) {
            // 如果返回的数据中real_name与id_card不为null，表示用户有填写实名信息
            if (!(resp.data.real_name && resp.data.id_card)) {
                $("#auth-warn").show();
            }
            //然后发请求获取房源数据
            $.get('/api_1_0/user/houses',function (resp) {
                if ("0" == resp.errno) {
                    //通过模板填充数据
                    $("#houses-list").html(template("houses-list-tmpl",{"houses":resp.data.houses}))
                }else{
                    $("#houses-list").html(template("houses-list-tmpl",{"houses":[]}))
                }
            })

        } else {
            alert(resp.errmsg);
        }
    }, "json");

});
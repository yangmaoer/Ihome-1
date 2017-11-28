function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


/*function logout() {
    $.ajax({
        url:"/api_1_0/session",
        type:'delete',
        headers:{
          'X-CSRFToken':getCookie('csrf-token')
        },
        dataType:'json',
        success:function(data){
            if (0 == data.errno) {
            location.href = "/";
            }
        }

    })
}*/

// 点击推出按钮时执行的函数
function logout() {
    $.ajax({
        url: "/api_1_0/session",
        type: "delete",
        dataType: "json",
        headers: {
            "X-CSRFToken": getCookie("csrf_token")
        },
        success: function (resp) {
            if ("0" == resp.errno) {
                location.href = "/index.html";
            }
        }
    });
}


$(document).ready(function(){
    $.get('/api_1_0/user/center',function (resp) {
        if (resp.errno=='4103'){
            location.href('/login.html')
        }else if('0'==resp.errno){
            $('#user-name').html(resp.data.name);
            $('#user-mobile').html(resp.data.mobile);
            //alert(resp.data.avatar);
            if (resp.data.avatar){
                $('#user-avatar').attr('src',resp.data.avatar)
            }
        }
    });

/*    $.get("/api_1_0/user", function(resp){
        // 用户未登录
        if ("4101" == resp.errno) {
            location.href = "/login.html";
        }
        // 查询到了用户的信息
        else if ("0" == resp.errno) {
            $("#user-name").html(resp.data.name);
            $("#user-mobile").html(resp.data.mobile);
            if (resp.data.avatar) {
                $("#user-avatar").attr("src", resp.data.avatar);
            }

        }
    }, "json");*/

});
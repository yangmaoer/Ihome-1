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
        headers: {
            "X-CSRFToken": getCookie("csrf_token")
        },
        dataType: "json",
        success: function (resp) {
            if ("0" == resp.errno) {
                location.href = "/index.html";
            }
        }
    });
}


$(document).ready(function(){

});
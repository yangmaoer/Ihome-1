function showSuccessMsg() {
    $('.popup_con').fadeIn('fast', function () {
        setTimeout(function () {
            $('.popup_con').fadeOut('fast', function () {
            });
        }, 1000)
    });
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function () {
    $('#form-avatar').submit(function (e) {
        e.preventDefault();
        $(this).ajaxSubmit({
            url: '/api_1_0/users/avatar',
            type: 'post',
            dataType: 'json',
            headers: {
                'X-CSRFToken': getCookie('csrf_token')
            },
            success: function (resp) {
                if (resp.errno == '0') {
                    var avatarurl = resp.data.avatar_url;
                    alert(avatarurl);
                    $('#user-avatar').attr('src', avatarurl)
                }else if(resp.errno == '4101'){
                    location.href='/index.html'
                } else {
                    alert(resp.errmsg)
                }
            }
        })
    });

        // 在页面加载是向后端查询用户的信息
    $.get("/api_1_0/user/center", function(resp){
        // 用户未登录
        if ("4101" == resp.errno) {
            location.href = "/login.html";
        }
        // 查询到了用户的信息
        else if ("0" == resp.errno) {
            $("#user-name").val(resp.data.name);
            if (resp.data.avatar) {
                $("#user-avatar").attr("src", resp.data.avatar);
            }
        }
    }, "json");

    $('#form-name').submit(function (e) {
        e.preventDefault();
        var name = $('#user-name').val();
        var req_data = {
            name: name
        };
        var req_json = JSON.stringify(req_data);
        $.ajax({
            url:'/api_1_0/users/name',
            type:'PUT',
            data:req_json,
            contentType:'application/json',
            dataType:'json',
            headers:{
                'X-CSRFToken': getCookie('csrf_token')
            },
            success:function (resp) {
                if (resp.errno == '0') {
                    $(".error-msg").hide();
                    showSuccessMsg();
                    //alert('保存成功')
                } else if ("4001" == data.errno) {
                    $(".error-msg").show();
                } else if ("4101" == data.errno) {
                    location.href = "/login.html";
                }
            }
        });

        /*$.ajax({
            url:"/api/v1.0/user/name",
            type:"PUT",
            data: JSON.stringify({name: name}),
            contentType: "application/json",
            dataType: "json",
            headers:{
                "X-CSRFTOKEN":getCookie("csrf_token")
            },
            success: function (data) {
                if ("0" == data.errno) {
                    $(".error-msg").hide();
                    showSuccessMsg();
                } else if ("4001" == data.errno) {
                    $(".error-msg").show();
                } else if ("4101" == data.errno) {
                    location.href = "/login.html";
                }
            }
        });*/

    })

});

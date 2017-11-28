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
                    $('#user-avatar').attr('src', avatarurl)
                } else {
                    alert(resp.errmsg)
                }
            }
        })
    });

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

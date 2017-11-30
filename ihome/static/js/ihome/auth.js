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
    $("#form-auth").submit(function (e) {
        e.preventDefault();
        var real_name = $("#real-name").val();
        var id_card = $("#id-card").val();
        if (real_name == "" || id_card == "") {
            $(".error-msg").show();
        }

        var data = {
            real_name: real_name,
            id_card: id_card
        };
        $.ajax({
            url: "/api_1_0/user/auth",
            type: 'post',
            contentType: 'application/json',
            data: JSON.stringify(data),
            dataType: 'json',
            headers: {
                "X-CSRFTOKEN": getCookie("csrf_token")
            },
            success: function (resp) {
                if (0 == resp.errno) {
                    $(".error-msg").hide();
                    // 显示保存成功的提示信息
                    showSuccessMsg();
                    $("#real-name").prop("disabled", true);
                    $("#id-card").prop("disabled", true);
                    $("#form-auth>input[type=submit]").hide();
                }
            }
        })
    });

    // 查询用户的实名认证信息
    $.get("/api_1_0/user/auth", function (resp) {
        // 4101代表用户未登录
        if ("4101" == resp.errno) {
            location.href = "/login.html";
        } else if ("0" == resp.errno) {
            // 如果返回的数据中real_name与id_card不为null，表示用户有填写实名信息
            if (resp.data.real_name && resp.data.id_card) {
                $("#real-name").val(resp.data.real_name);
                $("#id-card").val(resp.data.id_card);
                // 给input添加disabled属性，禁止用户修改
                $("#real-name").prop("disabled", true);
                $("#id-card").prop("disabled", true);
                // 隐藏提交保存按钮
                $("#form-auth>input[type=submit]").hide();
            }
        } else {
            alert(resp.errmsg);
        }
    }, "json");
});


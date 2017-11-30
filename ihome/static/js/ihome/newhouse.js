function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function(){
    // $('.popup_con').fadeIn('fast');
    // $('.popup_con').fadeOut('fast');
    $.get('/api_1_0/areas',function (resp) {
        if (resp.errno=='0') {
            var areas=resp.data;
            // alert(areas[0].id);
            // for (i=0; i<areas.length; i++){
            //     var area = areas[i];
            //     $("#area-id").append('<option value="'+ area.id +'">'+ area.name +'</option>');
            // } // 这种做法后端会导致查看网页源代码时直接可以看到区域信息,故需通过采用js模板获取
            var html = template("areas-temp", {areas: areas});
            $("#area-id").html(html);
        }else{
            alert(resp.errmsg);
        }
    },'json');

    $('#form-house-info').submit(function (e) {
        e.preventDefault();
        // 获取要请求的信息
        var data={};
        $('#form-house-info').serializeArray().map(function (x) {data[x.name]=x.value});

        // 将获取的设施id转换成列表处理
        var facility=[];
        $(":checked[name=facility]").each(function (index,x) {facility[index]=$(x).val()});
        data.facility=facility;

        $.ajax({
            url:'/api_1_0/house/info',
            type:'post',
            contentType:'application/json',
            data:JSON.stringify(data),
            dataType:'json',
            headers:{
                'X-CSRFToken':getCookie('csrf_token')
            },
            success:function (resp) {
                if (resp.errno=='4101'){
                    location.href='/index.html';
                }else if (resp.errno=='0'){
                    $("#form-house-info").hide();
                    $("#form-house-image").show();
                    $("#house-id").val(resp.data.house_id);
                }else{
                    alert(resp.errmsg);
                }
            }
        })
    });

    // 上传图片时,由于图片类型的原因,无法直接使用ajax进行上传,故采用ajaxsubmit方式进行上传
    $("#form-house-image").submit(function (e) {
        e.preventDefault();
        $(this).ajaxSubmit({
            url:'/api_1_0/house/img',
            type:'post',
            dataType:'json',
            headers:{
                'X-CSRFToken':getCookie('csrf_token')
            },
            success:function (resp) {
                if (resp.errno == "4101") {
                    location.href = "/login.html";
                } else if (resp.errno == "0"){
                    // $(".house-image-cons").attr('src', resp.data.img_url);
                    $(".house-image-cons").append('<img src="'+resp.data.img_url+'">');
                }else{
                    alert(resp.errmsg);
                }
            }

        })
    })

});
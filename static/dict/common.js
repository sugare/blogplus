/**
 * Created by song on 2017/4/5.
 */

/////////////////////index.html////////////////////////////////
// 登录验证码，点击转为验证码，再次点击更换验证码
function changeCode() {
    if ($('#imgCode').attr('src') == '') {
        $('#showImg').hide();
        $('#imgCode').attr('src', '/check_code');
        $('#imgCode').attr('src', '/check_code')

    } else {
        var link = $('#imgCode').attr('src');
        $('#imgCode').attr('src', link + '?');

//            var code = document.getElementById('imgCode');
//            code.src += '?';
    }
}


// 验证邮箱的正确性，发送邮件
function sendCode(ths) {
    $('#registerModal .error').remove();
    var username = $('#register_username').val();
    var email = $('#register_email').val();
    $.ajax({
        url: '/sendcode',
        type: 'POST',
        data: {register_username: username, register_email: email},
        dataType: 'json',
        success: function (arg) {
            if (arg.status) {
                //登陆成功，跳转
                console.log(arg.data)
            } else {
                $.each(arg.message, function (k,v) {
                    if (k == 'register_error') {
                        console.log(arg);
                        var tag = document.createElement('span');
                        tag.className = 'error';
                        tag.innerText = '该用户名或邮箱已经被注册过!';
                        $("#register_username").before(tag);
                    } else {
                        var tag = document.createElement('span');
                        tag.className = 'error';
                        tag.innerText = v;
                        $("#" + k + "").after(tag);
                        tag.innerText = v;
                        console.log(v);
                    }
                });
            }
        }
    });
}


// 用户提交登录信息
function submitLogin() {

    $('#loginModal .error').remove();
    var post_dict = {};
    $('.login-temp').each(function () {
        var input_val = $(this).val();
        var name_val = $(this).attr('name');
        post_dict[name_val] = input_val;
    });
    $.ajax({
        url: '/login',
        type: 'POST',
        data: post_dict,
        dataType: 'json',

        success:function (arg) {
            console.log(arg);
            //var obj = JSON.parse(arg);
            if (arg.status) {
                //登陆成功，跳转
                location.href = '/';
            } else {
                $.each(arg.message, function (k,v) {
                    var tag = document.createElement('span');
                    tag.className = 'error glyphicon glyphicon-remove form-control-feedback';
                    //tag.innerText = v;

                    $("#"+ k + "").after(tag)
                })
            }
        }
    })

}

// 用户提交注册信息
function sumitRegister() {

    $('#registerModal .error').remove();

    var post_dict = {};
    $('.register-temp').each(function () {
        var input_val = $(this).val();
        var name_val = $(this).attr('name');
        post_dict[name_val] = input_val;
    });

    console.log(post_dict);

    $.ajax({
        url: '/register',
        type: 'POST',
        data: post_dict,
        dataType: 'json',

        success: function (arg) {
            console.log(arg);
            // var obj = JSON.parse(arg);
            if (arg.status) {
                //注册成功，跳转
                location.href = '/';
            } else {
                // console.log(arg.message)
                $.each(arg.message, function (k,v) {
                    if (k == 'timeout') {
                        alert(v);
                        location.href = '/';
                    } else {
                        var tag = document.createElement('span');
                        tag.className = 'error glyphicon glyphicon-remove form-control-feedback';
                        //tag.innerText = v;
                        $("#" + k + "").after(tag);
                        console.log(v);
                    }
                })
            }
        }
    });
}

// 右栏的伸缩
$(function(){

    $('.panel-close').click(function(){
        $(this).parent().parent().parent().hide(300);
    });

    $('.collapse').on('hide.bs.collapse',function(){
        $(this).prev().find(".panel-collapse").removeClass('glyphicon-chevron-up').addClass('glyphicon-chevron-down');
    });

    $('.collapse').on('show.bs.collapse',function(){
        $(this).prev().find(".panel-collapse").removeClass('glyphicon-chevron-down').addClass('glyphicon-chevron-up');
    });

});


/////////////////////////article.html////////////////////////////////////////
// 打开评论表单
function openForm(ths) {
    var replayForm = $(ths).parent().parent().next();
    replayForm.toggleClass('hidden');
}

// 将评论内容送入后台，返回
function replyComment(ths) {
    var replayForm = $(ths).parent();
    var user_id = replayForm.attr('user_info_id');
    var reply_id = replayForm.attr('reply_id');
    var article_id = replayForm.attr('article_id');
    var comment_content = replayForm.children('textarea').val();

    if (comment_content.length >= 3) {
        $.ajax({
            url: '/comment',
            type: 'POST',

            data: {
                user_info_id: user_id,
                reply_id: reply_id,
                article_id: article_id,
                content: comment_content
            },

            dataType: 'json',

            success: function (arg) {
                if (arg.status) {
                    //登陆成功，跳转
                    console.log(arg.data);
                    location.href = '/articles/'+article_id;
                    // location.href = document.write(location.href)
                } else {
                    console.log(arg);
                }
            },
            error: function (arg) {
                if (arg.status == 403) {
                    alert('请先登录，啵啵');
                    $('#loginModal').modal('show');
                } else {
                    alert('wait for a moment, Thank you!');
                }

            }

        })
    } else {
        alert('评论区域不能小于5个字符！')
    }
}

//在编辑页面中展示 cataimg供选择
function choiceCataImg(sId) {
//    var oImg = document.getElementsByTagName('img');

    var oImg = $('.editor-show-cata-img img');
    for (var i = 0; i < oImg.length; i++) {
        if (oImg[i].id == sId) {
        oImg[i].previousSibling.previousSibling.checked = true;
        oImg[i].style.border = '1px solid #FF6600';
        } else {
        oImg[i].style.border = '1px solid #008800';

        }
    }
}
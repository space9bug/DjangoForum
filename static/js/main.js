$(document).ready(function () {
    $.imgLazyLoad();

    $("body").append('<div id="backtotop"><a href="#"></a></div>');
    var c = 100;
    var d = 500;

    $(window).scroll(function () {
        if ($(window).scrollTop() >= c) {
            $("#backtotop").addClass("visible uk-animation-slide-bottom")
        } else {
            $("#backtotop").removeClass("visible uk-animation-slide-bottom")
        }
    });
    $("#backtotop a").on("click", function () {
        $("html, body").animate({scrollTop: 0}, d);
        return false
    });

    $('#uploadFile').on('change', function (e) {
        var name = e.currentTarget.files[0].name;
        $("#uploadFileName").text(name);
    });
    $('#uploadAvator').on('change', function (e) {
        var name = e.currentTarget.files[0].name;
        $("#uploadAvatorName").text(name);
        var path = getobjecturl(e.currentTarget.files[0]);
        $("#my_avator").attr("src", path);
    });
    $('#userBackfile').on('change', function (e) {
        var name = e.currentTarget.files[0].name;
        var path = getobjecturl(e.currentTarget.files[0]);
        $("#userBackreal").attr("src", path);
    });

    $("#uploadVideo").click(function () {
        var textarea = $(".OwO-textarea");
        textarea.val(textarea.val() + "[video]在此输入内容!!!在此输入链接|在此输入封面[/video]")
    });
    $('#uploadVideoReal').on('change', function (e) {
        var name = e.currentTarget.files[0].name;
        $("#uploadVideoName").text(name);
    });
    $("#uploadMp3").click(function () {
        var textarea = $(".OwO-textarea");
        textarea.val(textarea.val() + "[mp3]在此输入内容!!!在此输入链接[/mp3]")
    });
    $("#uploadBiliBili").click(function () {
        var textarea = $(".OwO-textarea");
        textarea.val(textarea.val() + "[bilibili]在此输入内容!!!在此输入链接[/bilibili]")
    });
    $("#insertMarkdown").click(function () {
        var textarea = $(".OwO-textarea");
        textarea.val(textarea.val() + "[markdown]在此输入标题!!!在此输入Markdown[/markdown]")
    });
    toastr.options.positionClass = "toast-top-center";

    $(".fastcomment").keypress(function (e) {
        if (e.which === 13) {
            fastcomment($(this).attr("data-id"), $(this).val())
        }
    });
    var clipboard = new Clipboard('#sharebtn');
    clipboard.on('success', function (e) {
        toastr.info('复制链接成功！');
        e.clearSelection();
    });
});

function getobjecturl(file) {
    var url = null;
    if (window.createObjectURL != undefined) { // basic
        url = window.createObjectURL(file);
    } else if (window.URL != undefined) { // mozilla(firefox)
        url = window.URL.createObjectURL(file);
    } else if (window.webkitURL != undefined) { // webkit or chrome
        url = window.webkitURL.createObjectURL(file);
    }
    return url;
}

function publish() {
    let publish_submit = $("#publish-submit");
    $(publish_submit).text("等待中...");

    var content = $("div.post-new textarea").val();
    var category = $("div.post-new #category").val();
    var uploadfile = $("div.post-new #uploadFile")[0].files[0];
    var uploadvideofile = $("div.post-new #uploadVideoReal")[0].files[0];

    if (content.length < 3 || content.length > 50000) {
        toastr.error("提示信息", "内容少于3个字符，或者超出范围！");
        $(publish_submit).text("发送!");
        return false
    }
    if (uploadfile !== undefined && uploadfile.size > 4194304) {
        toastr.error("提示信息", "图片文件不能超过4m！");
        $(publish_submit).text("发送!");
        return false
    }
    if (uploadvideofile !== undefined && uploadvideofile.size > 5242880) {
        toastr.error("提示信息", "视频文件不能超过5m！");
        $(publish_submit).text("发送!");
        return false
    }

    var formData = new FormData();
    formData.append("content", content);
    formData.append("category", category);
    formData.append("uploadfile", uploadfile);
    formData.append("uploadvideofile", uploadvideofile);
    $(publish_submit).attr('disabled', true);
    $.ajax({
        type: "POST",
        dataType: "json",
        url: "/publish/",
        data: formData,
        processData: false,
        contentType: false,
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", $.cookie("csrftoken"))
        }, success: function (result) {
            if (result["code"] === 0) {
                toastr.error(result["msg"]);
            } else {
                toastr.info(result["msg"]);
                window.location.reload();
            }
            $(publish_submit).text("发送!");
            $(publish_submit).attr('disabled', false)
        }, error: function () {
        }
    })
}

function good(e) {
    var id = $(e).attr("data-id");
    var type = $(e).attr("data-type");
    $.ajax({
        type: "GET",
        dataType: "json",
        url: "/good/" + type + "/" + id,
        success: function (result) {
            if (result["code"] === 0) {
                toastr.error(result["msg"])
            } else {
                let likenumb = $(e).find(".likenumb-" + id).text();
                $(".likenumb-" + id).text((parseInt(likenumb) + 1) + "");
                toastr.info(result['msg']);
            }
        }, error: function () {
        }
    })
}

function reply(e) {
    let textarea = $("div.post-new textarea");
    let temptextarea = $("div.post-new #temp-textarea");
    let nickname = $(e).attr("data-author");
    let commid = $(e).attr("data-commid");
    $(textarea).attr("placeholder", "@" + nickname + " ");
    $(temptextarea).attr("placeholder", "@" + nickname + " ");
    $("#comment-parentid").val(commid)
}

function invite() {
    var towho = $("#towho").val();
    var formData = new FormData();
    formData.append("towho", towho);
    $.ajax({
        type: "POST",
        dataType: "json",
        url: "/invite/",
        data: formData,
        processData: false,
        contentType: false,
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", $.cookie("csrftoken"))
        }, success: function (result) {
            if (result["code"] === 0) {
                toastr.error(result["msg"]);
            } else {
                toastr.info(result["msg"]);
                window.location.reload();
            }
        }, error: function () {
        }
    })
}

function comment() {
    let comment_submit = $("#comment-submit");
    $(comment_submit).text("等待中...");

    var parentid = $("#comment-parentid").val();
    var threadid = $(comment_submit).attr("data-thread");

    var content = $("div.post-new textarea").val();
    var uploadfile = $("div.post-new #uploadFile")[0].files[0];

    if (content.length < 3 || content.length > 50000) {
        toastr.error("提示信息", "内容少于3个字符，或者超出范围！");
        $(publish_submit).text("回复!");
        return false
    }

    var formData = new FormData();
    formData.append("content", content);
    formData.append("parentid", parentid);
    formData.append("uploadfile", uploadfile);
    $(comment_submit).attr('disabled', true);
    $.ajax({
        type: "POST",
        dataType: "json",
        url: "/comment/" + threadid,
        data: formData,
        processData: false,
        contentType: false,
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", $.cookie("csrftoken"))
        }, success: function (result) {
            if (result["code"] === 0) {
                toastr.error(result["msg"]);
            } else {
                toastr.info(result["msg"]);
                window.location.reload()
            }
            $(comment_submit).text("回复!");
            $(comment_submit).attr('disabled', false)
        }, error: function () {
        }
    })
}

function paymarket(e) {
    let marketid = $(e).attr("data-id");
    $(e).text("支付中...");
    $(e).attr('disabled', true);
    $.ajax({
        type: "get",
        dataType: "json",
        url: "/paymarket/" + marketid,
        success: function (result) {
            if (result["code"] === 0) {
                toastr.error(result["msg"]);
                $(e).text("立即购买");
                $(e).attr('disabled', false);
            } else {
                toastr.info(result["msg"]);
                window.location.reload();
            }
        }, error: function () {
        }
    })
}

function sendactive() {
    var sendactive = $("#sendactive");
    sendactive.unbind('click');
    sendactive.text("发送中...");
    $.ajax({
        type: "GET",
        dataType: "json",
        url: "/active/",
        success: function (result) {
            toastr.info(result["msg"]);
            sendactive.text("发送完毕！")
        }, error: function () {
        }
    })
}

function signpoint() {
    $.ajax({
        type: "get",
        dataType: "json",
        url: "/signpoint/",
        success: function (result) {
            toastr.info(result["msg"]);
            window.location.reload();
        }, error: function () {
        }
    })
}

function setniminswh(e) {
    let niminflag = $(e).attr("data-niminflag");
    $.ajax({
        type: "get",
        dataType: "json",
        url: "/setniminswh/" + niminflag,
        success: function (result) {
            var button = $(e).find(".uk-switch-button");
            if ($(button).hasClass("on")) {
                $(e).attr("data-niminflag", 1);
                $(button).removeClass("on");
            } else {
                $(e).attr("data-niminflag", 0);
                $(button).addClass("on");
            }
            toastr.info(result["msg"])
        }, error: function () {
        }
    })
}

function setbackswih(e) {
    let niminflag = $(e).attr("data-backflag");
    $.ajax({
        type: "get",
        dataType: "json",
        url: "/setbackswih/" + niminflag,
        success: function (result) {
            var button = $(e).find(".uk-switch-button");
            if ($(button).hasClass("on")) {
                $(e).attr("data-backflag", 1);
                $(button).removeClass("on");
            } else {
                $(e).attr("data-backflag", 0);
                $(button).addClass("on");
            }
            toastr.info(result["msg"])
        }, error: function () {
        }
    })
}

function setlocation(e) {
    let localflag = $(e).attr("data-localflag");
    if (localflag == 0) {
        $.ajax({
            type: "get",
            dataType: "json",
            url: "/setlocation/0",
            success: function (result) {
                var button = $(e).find(".uk-switch-button");
                if ($(button).hasClass("on")) {
                    $(e).attr("data-localflag", 1);
                    $(button).removeClass("on");
                } else {
                    $(e).attr("data-localflag", 0);
                    $(button).addClass("on");
                }
                toastr.info(result["msg"])
            }, error: function () {
            }
        })
    } else {
        toastr.info("获取位置中,请等待片刻...");
        var geolocation = new BMap.Geolocation();
        geolocation.getCurrentPosition(function (r) {
            if (this.getStatus() === BMAP_STATUS_SUCCESS) {
                $.ajax({
                    type: "get",
                    dataType: "json",
                    url: "/setlocation/1?lng=" + r.point.lng + "&lat=" + r.point.lat,
                    success: function (result) {
                        var button = $(e).find(".uk-switch-button");
                        if ($(button).hasClass("on")) {
                            $(e).attr("data-localflag", 1);
                            $(button).removeClass("on");
                        } else {
                            $(e).attr("data-localflag", 0);
                            $(button).addClass("on");
                        }
                        toastr.info(result["msg"])
                    }, error: function () {
                    }
                })
            } else {
            }
        }, {enableHighAccuracy: true});
    }
}

function setrecvemail(e) {
    let recvflag = $(e).attr("data-recvflag");
    $.ajax({
        type: "get",
        dataType: "json",
        url: "/setrecvemail/" + recvflag,
        success: function (result) {
            var button = $(e).find(".uk-switch-button");
            if ($(button).hasClass("on")) {
                $(e).attr("data-recvflag", 1);
                $(button).removeClass("on");
            } else {
                $(e).attr("data-recvflag", 0);
                $(button).addClass("on");
            }
            toastr.info(result["msg"])
        }, error: function () {
        }
    })
}

function fastcomment(id, content) {
    if (content.length < 3 || content.length > 50000) {
        toastr.error("提示信息", "内容少于3个字符，或者超出范围！");
        return false
    }
    var formData = new FormData();
    formData.append("content", content);
    $.ajax({
        type: "POST",
        dataType: "json",
        url: "/fastcomment/" + id,
        data: formData,
        processData: false,
        contentType: false,
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", $.cookie("csrftoken"))
        }, success: function (result) {
            if (result["code"] === 0) {
                toastr.error(result["msg"])
            } else {
                toastr.info(result["msg"]);
                window.location.reload()
            }
        }, error: function () {
        }
    })
}

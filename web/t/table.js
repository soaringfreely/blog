/**
 * Created by xueyan on 2017/5/19.
 */

function CheckAll() {
    $(':checkbox').prop('checked',true);
}
function CancleAll() {
    $(':checkbox').prop('checked',false);
}
function CheckReverse() {
    $(':checkbox').each(function(){
        var v = $(this).prop('checked')?false:true;
        $(this).prop('checked',v);
    })
}
function EditMode() {
     $(':checkbox').each(function(){
        if($(this).prop('checked')){
            var tr = $(this).parent().parent();
            var host = tr.children("input:eq(1)");
            var port = tr.children("input:eq(2)");
            host.removeClass("noline");
            host.addClass("haveline");
            host.removeAttr("readonly");
            // $("input").removeClass("noline");
            // $("input").addClass("haveline");
            // $("input").removeAttr("readonly");
        }
     })
}
function SaveMode() {
     $(':checkbox').each(function(){
        if($(this).prop('checked')){
            $("input").removeClass("haveline");
            $("input").addClass("noline");
            $("input").attr("readonly","readonly");
        }
     })
}

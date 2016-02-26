// Start Editing
$.fn.editable.defaults.mode = 'inline';
$.fn.editable.defaults.ajaxOptions = {type: "post", dataType: "json"};
$('.editable-tabs').editable({
    url: '/_edit_tab_title'
});
$('.toggle-editing').click(function () {
    var parentTitle = $(this).parent().parent().find(".editable-tabs");
    var parentTitleId = parentTitle.attr('id');
    $('#' + parentTitleId).editable('toggleDisabled');
});
$(document).ready(function () {
    $('.editable-tabs').editable('toggleDisabled');
});
$('.tabs-link').on('click', function (event) {
    if (!$(this).hasClass('editable-disabled')) {
        event.preventDefault();
    }
    else {
    }
});
// End Editing

// Start Deleting
$('.remove-tabset-button').on('click', function () {
    var parentGroup = $(this).parent().parent();
    var parent = parentGroup.find(".editable-tabs");
    var parentId = parent.attr('data-pk');
    swal({
        title: "Are you sure?",
        text: "You will not be able to recover this tab set!",
        type: "warning",
        showCancelButton: true,
        confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, delete it!",
        showLoaderOnConfirm: true,
        closeOnConfirm: false
    }, function (isConfirm) {
        if (isConfirm) {
            $.post('/_delete_tab_set', {tabSetId: parentId}, function() {
            }).done(function (data) {
                swal("Deleted!", "Your tab set has been deleted.", "success");
                parentGroup.detach();
                var tabsSetCount = $('.tab-set-count');
                var tabsCount = parseInt(tabsSetCount.text().replace(/\D/g,'')) - 1;
                tabsSetCount.text('Found ' + tabsCount + ' tab sets');
            }).fail(function (data) {
                swal("Failed", "Your tab set could not be deleted.", "error");
            });
        }
    });
});
// End Deleting
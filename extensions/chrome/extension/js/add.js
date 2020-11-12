var baseUrl = 'http://localhost:5000/api/';
var appUrl = 'http://localhost:5000/manager/bookmark/';


function getTags() {
    var query = {
        active: true,
        currentWindow: true
    };
    chrome.storage.sync.get(["useremail", "userkey"], function(items) {
        chrome.tabs.query(query, function(tabs) {
            require(['/libs/superagent.min.js'], function(request) {
                request
                    .post(baseUrl + "checkinfo")
                    .send({
                        email: items.useremail,
                        apikey: items.userkey,
                        url: tabs[0].url
                    })
                    .end(function(res) {
                        if (res.body.message == 'You have this URL bookmarked') {
                            $('#tags').attr('value', res.body.tags);
                            tagOptions = res.body.tagopts.split(',');
                            tagOptionsArr = [];
                            for (var i = 0; i < tagOptions.length; i++) {
                                tagOptionsArr.push({'text': tagOptions[i], 'value': tagOptions[i]});
                            }
                            $('#tags').selectize({
                                plugins: ['remove_button', 'restore_on_backspace'],
                                delimiter: ',',
                                persist: false,
                                options: tagOptionsArr,
                                create: function(input) {
                                    return {
                                        value: input,
                                        text: input
                                    };
                                }
                            });
                            $('#myButton').attr('bookmark_id', res.body.id);
                            $('#trashButton').attr('bookmark_id', res.body.id);
                            $('#readButton').removeClass('hidden').attr('href', appUrl + 'read/' + res.body.id);
                            $('#contextButton').removeClass('hidden').attr('href', appUrl + 'context/' + res.body.id);
                        } else {
                            $('#tags').selectize({
                                plugins: ['remove_button', 'restore_on_backspace'],
                                delimiter: ',',
                                persist: false,
                                create: function(input) {
                                    return {
                                        value: input,
                                        text: input
                                    };
                                }
                            });
                        }
                    });
            });
        });
    });
}

getTags();


$('#myButton').on('click', function(e) {
        e.preventDefault(); // Prevents reload on submit
        $self = $(this);
        chrome.storage.sync.get(["useremail", "userkey"], function(items) {
        require(['/libs/superagent.min.js'], function(request) {
            request
                .post(baseUrl + "edit")
                .send({
                    email: items.useremail,
                    apikey: items.userkey,
                    id: $self.attr('bookmark_id'),
                    tags: encodeURIComponent($('#tags').attr('value'))
                })
                .end(function(res) {
                    if (res.body.message === 'Bookmark Modified') {
                        $('#bookmarkUpdatedAlert').removeClass('hidden');
                    }
                });
            });
        });
    });

$('#readButton').on('click', function(e) {
    var $self = $(this);
    e.preventDefault(); // Prevents reload on submit
    chrome.tabs.create({url: $self.attr('href')});
});

$('#contextButton').on('click', function(e) {
    var $self = $(this);
    e.preventDefault(); // Prevents reload on submit
    chrome.tabs.create({url: $self.attr('href')});
});

$('#logoutButton').on('click', function(e) {
    e.preventDefault(); // Prevents reload on submit
    chrome.storage.sync.remove(["useremail", "userkey"]);
    $('#logoutSuccessAlert').removeClass('hidden');
    $('.selectize-input').remove();
    $('#myButton').addClass('hidden');
    $('#logoutButton').addClass('hidden');
    $('hr').remove();
    var query = {};
    chrome.tabs.query(query, function(tabs) {
        for (var i = 0; i < tabs.length; i++) {
            chrome.pageAction.setPopup({
                tabId: tabs[i].id,
                popup: '../popup-login.html'
            });
        }
    });
});

$('#trashButton').on('click', function(e)  {
    e.preventDefault();
    $self = $(this);
    var query = {
        active: true,
        currentWindow: true
    };
    chrome.storage.sync.get(['useremail', 'userkey'], function (items) {
        require(['/libs/superagent.min.js'], function(request) {
            request
            .post(baseUrl + 'delete')
            .send({
                email: items.useremail,
                apikey: items.userkey,
                id: $self.attr('bookmark_id')
            })
            .end(function(res) {
                if (res.body.message === 'Bookmark Deleted') {
                    $('#bookmarkDeletedAlert').removeClass('hidden');
                    $self.remove();
                    $('#readButton').remove();
                    $('#myButton').remove();
                    $('.selectize-input').remove();
                    $('#logoutButton').remove();
                    chrome.tabs.query(query, function(tabs) {
                    chrome.pageAction.setPopup({tabId: tabs[0].id, popup: ''});
                    chrome.pageAction.setIcon({tabId: tabs[0].id, path: '../icon1.png'});
                    chrome.pageAction.setTitle({tabId: tabs[0].id, title: 'This bookmark was deleted. Click to bookmark again'});
                });
                }
            });
        });
    });
});
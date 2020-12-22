var baseUrl = 'http://localhost:5000/api/';

$('#myButton').on('click', function(e) {
    e.preventDefault(); // Prevents reload on submit
    var userEmail = $('#userEmail').val();
    var userAK = $('#userAk').val();
    if (userEmail === "" || userAK === "") {
        $('#loginEmptyAlert').removeClass('hidden');
    } else {
        var $btn = $(this).button('loading');
        require(['/libs/superagent.min.js'], function(request) {
            request
                .post(baseUrl + "authenticate")
                .send({
                    email: userEmail,
                    apikey: userAK
                })
                .end(function(res) {
                    if (res.status === 200) {
                        chrome.storage.sync.set({
                            "useremail": userEmail,
                            "userkey": userAK
                        });
                        $('#loginSuccessAlert').removeClass('hidden');
                        $('#myButton').addClass('hidden');
                        $('#loginEmptyAlert').addClass('hidden');
                        $('#loginFailedAlert').addClass('hidden');
                        $('#userEmail').addClass('hidden');
                        $('#userAk').addClass('hidden');
                        var query = {};
                        chrome.tabs.query(query, function(tabs) {
                            for (var i = 0; i < tabs.length; i++) {
                            chrome.pageAction.setPopup({
                                tabId: tabs[i].id,
                                popup: ''
                            });
                        }
                        });
                    } else {
                        $('#loginFailedAlert').removeClass('hidden');
                    }
                });
        });
        $btn.button('reset');
    }
});
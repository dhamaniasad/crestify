var baseUrl = "http://localhost:5000/api/"; // The URL for the API

function tabContextMenuonClick(info, tab) {
    var query = {
        currentWindow: true
    };
    chrome.tabs.query(query, function (tabs) {
        var tabsData = Array();
        for (tab in tabs) {
            tab = parseInt(tab);
            if (typeof tab === "number") {
                var url = tabs[tab]['url'];
                var title = tabs[tab]['title'];
                if (url.startsWith('http')) {
                    var tabData = {'url': url, 'title': title};
                    tabsData.push(tabData);
                }
                else {

                }
            }
        }
        chrome.storage.sync.get(["useremail", "userkey"], function (items) {
            if (typeof items.useremail !== 'undefined') {
                require(['/libs/superagent.min.js'], function (request) {
                    request
                        .post(baseUrl + "tabs/add")
                        .send({
                            email: encodeURIComponent(items.useremail),
                            apikey: encodeURIComponent(items.userkey),
                            tabs: encodeURIComponent(JSON.stringify(tabsData))
                        })
                        .end(function (err, res) {
                            if (err === null) {
                                chrome.tabs.create({url: 'http://localhost:5000/manager/tabs/new?id=' + res.body.id});
                            }
                        });
                });
            }
        });
    });
}

var tabContextMenu = chrome.contextMenus.create({"title": "Save Open Tabs", "onclick": tabContextMenuonClick});

// Fired whenever the URL in the address bar changes, used to show the bookmark icon
chrome.tabs.onUpdated.addListener(function (id, changeInfo, tab) {
    if (tab.url.substring(0, 9) != "chrome://") {
        chrome.storage.sync.get(["useremail", "userkey"], function (items) {
            if (typeof items.useremail === 'undefined') {
                chrome.pageAction.show(tab.id);
                chrome.pageAction.setIcon({tabId: tab.id, path: 'icon1.png'});
                chrome.pageAction.setPopup({tabId: tab.id, popup: 'popup-login.html'});
                chrome.pageAction.setTitle({
                    tabId: tab.id,
                    title: 'Click to login'
                });
            }
            else {
                require(['/libs/superagent.min.js'], function (request) {
                    request
                        .post(baseUrl + "check")
                        .send({
                            email: encodeURIComponent(items.useremail),
                            apikey: encodeURIComponent(items.userkey),
                            url: encodeURIComponent(tab.url)
                        })
                        .end(function (err, res) {
                            if (err === null) {
                                if (res.body.message == 'You have this URL bookmarked') {
                                    chrome.pageAction.show(tab.id);
                                    chrome.pageAction.setIcon({tabId: tab.id, path: 'icon2.png'});
                                    chrome.pageAction.setTitle({
                                        tabId: tab.id,
                                        title: 'This page was bookmarked ' + res.body.added
                                    });
                                    chrome.pageAction.setPopup({tabId: tab.id, popup: 'popup-add.html'});
                                }
                                else if (res.status === 401) {
                                    chrome.pageAction.show(tab.id);
                                    chrome.pageAction.setPopup({tabId: tab.id, popup: 'popup-login.html'});
                                    chrome.pageAction.setTitle({
                                        tabId: tab.id,
                                        title: 'Click to login'
                                    });
                                }
                                else {
                                    chrome.pageAction.show(tab.id);
                                    chrome.pageAction.setIcon({tabId: tab.id, path: 'icon1.png'});
                                    chrome.pageAction.setPopup({tabId: tab.id, popup: ''});
                                    chrome.pageAction.setTitle({
                                        tabId: tab.id,
                                        title: 'Click to bookmark'
                                    });
                                }
                            }
                            else {
                                chrome.pageAction.show(tab.id);
                                chrome.pageAction.setIcon({tabId: tab.id, path: 'icon1.png'});
                                chrome.pageAction.setPopup({tabId: tab.id, popup: ''});
                                chrome.pageAction.setTitle({
                                    tabId: tab.id,
                                    title: 'Click to bookmark'
                                });
                            }
                        });
                });
            }
        });
    }
});


// Fired whenever the bookmark pageAction is clicked, used to send add request
chrome.pageAction.onClicked.addListener(function (tab) {
    chrome.pageAction.setIcon({tabId: tab.id, path: 'progress.png'});
    chrome.storage.sync.get(["useremail", "userkey"], function (items) {
        require(['/libs/superagent.min.js'], function (request) {
            request
                .post(baseUrl + "add")
                .send({
                    email: encodeURIComponent(items.useremail),
                    apikey: encodeURIComponent(items.userkey),
                    url: encodeURIComponent(tab.url),
                    title: encodeURIComponent(tab.title)
                })
                .end(function (err, res) {
                    if (err === null) {
                        if (res.body.message == 'URL bookmarked') {
                            chrome.pageAction.setIcon({tabId: tab.id, path: 'icon2.png'});
                            chrome.pageAction.setTitle({tabId: tab.id, title: 'This page was bookmarked just now'});
                            chrome.pageAction.setPopup({tabId: tab.id, popup: 'popup-add.html'});
                        } else {
                            chrome.pageAction.setIcon({tabId: tab.id, path: 'icon1.png'});
                        }
                    }
                    else {
                        chrome.pageAction.setIcon({tabId: tab.id, path: 'icon1.png'});
                        chrome.pageAction.setPopup({tabId: tab.id, popup: ''});
                        chrome.pageAction.setTitle({
                            tabId: tab.id,
                            title: 'Click to bookmark'
                        });
                    }
                });
        });
    });
});
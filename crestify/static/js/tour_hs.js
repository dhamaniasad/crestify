// Define the tour!
var tour = {
    id: "tour",
    steps: [
        {
            title: "Adding a bookmark",
            content: "Click this button to add a bookmark. Go ahead, try it!" +
            " You can also use our <a href='https://chrome.google.com/webstore/detail/crestify/afhekhbgacigmlndepbnppnpbhgdalfp'>Chrome</a>, " +
            "<a href='https://addons.opera.com/en/extensions/details/crestify/'>Opera</a>, and " +
            "<a href='https://addons.mozilla.org/en-US/firefox/addon/crestify/'>Firefox</a> extensions for simple 1-click bookmarking!",
            target: "new_bmark_btn",
            placement: "right"
        },
        {
            title: "Saved tab sets",
            content: "You can save your open tabs into a collection using the extension. Once you do that, you can view your saved tabs in here! To save a tab set, right click on a blank spot on the page and hit 'Save Open Tabs'.",
            target: "view_tabs_btn",
            placement: "bottom"
        },
        {
            title: "Powerful search",
            content: "You can search for bookmarked pages using title, description, url, tags, even the entire text of the page!",
            target: "search_form",
            placement: "bottom"
        },
        {
            title: "Filter using tags",
            content: "You can filter your bookmarks using their tags. You can also combine multiple tags and cut & slice through your bookmarks like a ninja!",
            target: "tags_panel_title",
            placement: "bottom"
        },
        {
            title: "Adjust your settings",
            content: "All of your settings can be accessed by clicking the gear icon. You can change your credentials, bookmarks displayed per page, and other settings in here.",
            target: "settings_btn",
            placement: "right"
        },
        {
            title: "Import your bookmarks",
            content: "You can import your bookmarks from Pocket, Pinboard, Instapaper, Readability, or your browser from within the settings.",
            target: "settings_btn",
            placement: "right"
        },
        {
            title: "Your bookmarks",
            content: "All your bookmarks are displayed here. Clicking on one will expand it to show its archives, tags, and reader view, context view, and sharing view links.",
            target: "bookmarks_list_block",
            placement: "left"
        },
        {
            title: "Your bookmarks",
            content: "You can view your older or newer bookmarks by going to pages with a higher or lower number respectively.",
            target: "bookmark_pagination_block",
            placement: "top"
        },
        {
            title: "Browser Extensions",
            content: "A single click on the extension icon will bookmark the page. Another click will allow you to add tags/ access the context view. If you visit a page you already have bookmarked, the extension icon will change color, and a click will allow you to add tags/access context view.",
            target: "logo_text",
            placement: "bottom"
        }
    ]
};

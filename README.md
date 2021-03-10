# Crestify
### Intelligent Bookmarking

[🎉 ANNOUNCEMENT: Crestify is available as a hosted service. Check it out here!](https://www.crestify.com)

<img width="946" alt="Crestify Features" src="https://user-images.githubusercontent.com/4560482/110683703-530f7700-8202-11eb-8522-5929909864fb.png">

### Works On
<img width="222" alt="Supported Browsers" src="https://user-images.githubusercontent.com/4560482/110683989-9ec22080-8202-11eb-8075-bdb987cbae91.png">


### About

Crestify is a self-hosted bookmarking service that does it all. There are a lot of bookmarking services out there today, and all of them do one thing or the other. With Crestify, you get the whole package. 

#### Features

* 1 click bookmarking with extensions for Chrome, Firefox, and Opera
* An API so you can make your own extensions
* Archiving to save bookmarks from [link rot](http://www.gwern.net/Archiving%20URLs#link-rot)
* Filtering bookmarks by titles, descriptions, urls, tags, or even the entire text of the page
* Automatic saving of the full text of your browsing history into a private search engine
* Cleaning up articles to make them easier to read (Reader Mode)
* Public links you can share or cite so you don't end up linking to dead pages
* Saving the open tabs from your browser for coming back to them later
* Categorizing bookmarks via tags
* Context filtering so you can get back into the flow of how you came across a particular page
* Importing bookmarks from your current browser, or your Pocket, Instapaper, Raindrop & Pinboard accounts

And best of all, Crestify is fully open source, so you can host your own instance, modify Crestify to your heart's content, and generally do whatever you like with it! 

### Quick Start

To get started with Crestify, try out our Vagrant image!

```bash
$ git clone https://github.com/crestify/crestify.git && cd crestify
$ pip install fabric
$ fab vagrant_init
```

*side note: In order to install Fabric, you might need to install the `libffi-dev` & `libssl-dev` packages on Ubuntu.*

That's it! Open your browser, head to `http://localhost:4545`, create an account, and you'll be good to go!

To get the latest updates to Crestify, run:
<img width="236" alt="Screenshot 2021-03-11 at 12 41 51 AM" src="https://user-images.githubusercontent.com/4560482/110683932-94a02200-8202-11eb-9da1-6673983c5531.png">

```bash
fab update
```

And the latest updates from the master branch will be applied.

For manual install, see `INSTALL.md`.

### Tech Stack

Crestify is built on the Flask framework and written in Python 3.

* Languages: Python 3 & Javascript (Extensions)
* Framework: Flask
* Database: Crestify uses PostgreSQL as its database, and takes advantage of the full-text search capabilities of Postgres. Redis is used as a temp database for holding incoming tab saves
* Message Queue: Redis is used as a message queue for asynchronously-run tasks related to bookmarking
* Browser: Crestify uses Puppeteer to generate the DOM like a browser does for full-text extraction and readability view generation

### License

Crestify is BSD licensed. See `LICENSE` for more details.

---

### Note

A new version of Crestify with an updated design, new and improved features, based on Python 3, and installable through Docker will be available soon!

[Until then, you can check out the hosted SaaS version here:](https://www.crestify.com) www.crestify.com

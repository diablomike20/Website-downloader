## Complete Website Downloader 💾
Download the complete source code of any website (including all assets) 🔨.

👉 Live Demo: https://website-downloader.onrender.com

![enter image description here](https://github.com/AhmadIbrahiim/Website-downloader/blob/master/public/Record.gif?raw=true)
<div align="center">

  <a href="">![CodeFactor](https://www.codefactor.io/repository/github/ahmadibrahiim/website-downloader/badge)</a>

</div>

## Description 📒
 Website downloader works with `wget` and `archiver` to download all websites assets and compress then sends it back to the user through socket channel
 
 **wget params the being used**
 
 `wget --mirror --convert-links --adjust-extension --page-requisites 
--no-parent http://example.org`

 **Explanation of the various flags:**

 - --mirror – Makes (among other things) the download recursive.
- --convert-links – convert all the links (also to stuff like CSS stylesheets) to relative, so it will be suitable for offline viewing.
- --adjust-extension – Adds suitable extensions to filenames (html or css) depending on their content-type.
- --page-requisites – Download things like CSS style-sheets and images required to properly display the page offline.
- --no-parent – When recursing do not ascend to the parent directory. It useful for restricting the download to only a portion of the site

## fu_6 Cudy Emulator Forensic mode

This fork now contains a Cudy-specific read-only crawler for the public emulator trees under:

```text
https://support.cudy.com/emulator/<MODEL>/
```

Unlike a normal `wget --mirror`, it also scans downloaded HTML/JS for LuCI routes and reproduces the public emulator bootstrap's static route mapping. This is useful for snapshots that are not reachable by simply clicking through the visible menus.

It preserves response bytes exactly and writes SHA-256 hashes and a route inventory.

### Run

```bash
npm run cudy-forensic -- \
  --url https://support.cudy.com/emulator/C200P/ \
  --output cudy-forensic-output/C200P
```

Useful limits:

```bash
npm run cudy-forensic -- \
  --url https://support.cudy.com/emulator/C200P/ \
  --max-requests 2500 \
  --max-bytes 67108864 \
  --delay-ms 100 \
  --timeout-ms 20000
```

The output contains:

```text
raw/                         byte-exact public responses
fu_6-inventory.csv           URL/status/MIME/size/SHA256/local path
fu_6-all-luci-routes.txt     LuCI routes found in HTML/JS
fu_6-hidden-luci-routes.txt  routes mapped to emulator snapshots
fu_6-unresolved.txt          failed/non-2xx URLs
fu_6-findings.json           firmware/build/model/URL leads
fu_6-run.json                run settings and safety record
```

The crawler is intentionally conservative: **GET only**, one selected emulator-model subtree only, known destructive/action routes are skipped, and it does not do authentication bypass, brute force, firmware version guessing or timestamp spraying.

Run the route-mapping tests with:

```bash
npm run test:cudy
```

### Deploy on cloud providers
[![Run on Replit](https://binbashbanana.github.io/deploy-buttons/buttons/remade/replit.svg)](https://replit.com/github/AhmadIbrahiim/Website-downloader)
[![Remix on Glitch](https://binbashbanana.github.io/deploy-buttons/buttons/remade/glitch.svg)](https://glitch.com/edit/#!/import/github/AhmadIbrahiim/Website-downloader)
[![Deploy on Railway](https://binbashbanana.github.io/deploy-buttons/buttons/remade/railway.svg)](https://railway.app/new/template?template=https://github.com/AhmadIbrahiim/Website-downloader)
[![Deploy to Cyclic](https://binbashbanana.github.io/deploy-buttons/buttons/remade/cyclic.svg)](https://app.cyclic.sh/api/app/deploy/AhmadIbrahiim/Website-downloader)
[![Deploy to Koyeb](https://binbashbanana.github.io/deploy-buttons/buttons/remade/koyeb.svg)](https://app.koyeb.com/deploy?type=git&repository=github.com/AhmadIbrahiim/Website-downloader&branch=main&name=Website-downloader)
[![Deploy to Render](https://binbashbanana.github.io/deploy-buttons/buttons/remade/render.svg)](https://render.com/deploy?repo=https://github.com/AhmadIbrahiim/Website-downloader)


## Requirements 📦

- Node.js 16 or newer
- `wget` on the `PATH`. The app shells out to it, and nothing will download without it:
  - Debian/Ubuntu: `apt install wget`
  - macOS: `brew install wget`
  - Windows: `winget install JernejSimoncic.Wget`

## How to run it 🤔

- `git clone https://github.com/diablomike20/Website-downloader.git`
- `cd Website-downloader`
- `$ npm install`
- `$ npm start`
- `http://localhost:3000/`

### Optional settings

| Variable | Default | What it does |
| --- | --- | --- |
| `PORT` | `3000` | Port the server listens on |
| `DOWNLOAD_QUOTA` | `100m` | Size ceiling passed to wget, so one request cannot fill the disk |
| `DOWNLOAD_TIMEOUT_MS` | `300000` | How long a single download may run before it is stopped |



# How To Contribute:
 - Open Issue(s) with any bugs you notice.
 - Please create Pull Requests if you think it would be an added value towards our program.

## Liked it ? You can buy a coffee:

<a href="https://www.buymeacoffee.com/aibrahim" target="_blank"><img src="https://www.buymeacoffee.com/aibrahim" alt=""></a>

Thank you,

Email: me@ahmed-ibrahim.com

https://www.ahmed-ibrahim.com

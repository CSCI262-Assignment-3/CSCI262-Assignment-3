# CSCI262-Assignment-3

A phishing prevention proxy. Requests pass through the proxy, where each URL is
checked against a blocklist of known phishing URLs and a scikit-learn ML model.
Phishing URLs get a `403` block page instead of being forwarded.

## How it works

```
browser/curl  ──►  mitmproxy (VM 192.168.56.10, port 8080)  ──►  origin server
                       │
                       ├─ lib/proxy_addon.py   inspects each request
                       ├─ lib/detector.py      blocklist check + ML score
                       ├─ lib/model.py         scikit-learn model (HuggingFace)
                       └─ lib/logger.py        writes logs.txt
```

- **Not phishing:** the addon does nothing, mitmproxy forwards the request and
  relays the response back to the client.
- **Phishing:** the addon returns a `403` page directly, the request is never
  forwarded.
- **HTTPS (`CONNECT`):** rejected with a `403` explanation — this demo only
  inspects plain HTTP URLs.

## Run the demo in a VM

Install both of these first:

- **VirtualBox:** <https://www.virtualbox.org/wiki/Downloads>
- **Vagrant:** <https://developer.hashicorp.com/vagrant/install>

Then, from the project folder:
## Diagrams

The flow is documented with [PlantUML](https://plantuml.com/) sources in
`docs/`, with rendered images next to them.

| Diagram | Source | Image |
| --- | --- | --- |
| Request flow (activity diagram) | [`docs/flow.puml`](docs/flow.puml) | ![Request flow](docs/flow.png) |
| Request sequence | [`docs/sequence.puml`](docs/sequence.puml) | ![Request sequence](docs/sequence.png) |
| Components | [`docs/component.puml`](docs/component.puml) | ![Components](docs/component.png) |

Regenerate the images after editing a `.puml` file:

```bash
plantuml -tpng docs/*.puml                            # needs Graphviz for layout
plantuml -tpng -Playout=smetana docs/*.puml           # pure-Java fallback
```

## Run the demo with Docker

```bash
vagrant up
```

This builds a Debian 12 VirtualBox VM at `192.168.56.10` and runs the proxy on
port `8080`, starting it automatically whenever the VM boots. The ML model is
downloaded while the VM is being set up, so the proxy needs no network to load
it at runtime.

Run `vagrant provision` after changing the code to copy it into the VM,
`vagrant halt` to stop the VM and `vagrant destroy` to delete it.

### Test it with curl

```bash
# Benign URL -> passes through, real page comes back (200)
curl -x http://192.168.56.10:8080 http://example.com

# Blocklisted URL -> 403 block page
curl -x http://192.168.56.10:8080 http://sus.com/

# ML-flagged URL -> 403 block page
curl -x http://192.168.56.10:8080 http://clubedemilhagem.com/home.php

# HTTPS is not inspected -> CONNECT tunnel refused
curl -x http://192.168.56.10:8080 https://example.com
```

On Windows, use `curl.exe` so PowerShell doesn't run its own `curl` alias.

### Test it with a browser

1. Start the VM (see above).
2. In Firefox: Settings → General → Network Settings →
   Manual proxy configuration → HTTP Proxy `192.168.56.10`, port `8080`.
3. Visit `http://sus.com` (blocked) or `http://example.com` (loads normally).

### Logs

Every access attempt is recorded in `logs.txt` (inside the VM at
`/opt/proxy/logs.txt`):

```
[!!!] [2026-10-19 01:11:59+11:00]: 'sus.com' accessed 'http://sus.com/'
[...] [2026-10-19 01:11:46+11:00]: 'example.com' accessed 'http://example.com/'
```

Run `vagrant ssh -c "tail -f /opt/proxy/logs.txt"` to watch requests as they
happen.

## Configuration

- **Blocklist:** `data/phishing_urls.txt`, one URL per line (scheme-stripped).
- **ML threshold:** `Detector(..., threshold=0.9)` in `lib/detector.py`.
- **Block page:** `BLOCK_PAGE` in `lib/proxy_addon.py`.

## Local development

```bash
uv sync
uv run python test_driver.py     # try the detector interactively
uv run mitmdump -s lib/proxy_addon.py   # run the proxy without the VM
```

## Limitations

- Only plain HTTP URLs are inspected; HTTPS traffic cannot be inspected without
  a man-in-the-middle certificate, so `CONNECT` tunnels are rejected instead.
- The ML model can produce false positives/negatives; the threshold in
  `lib/detector.py` balances this.

# Stage 1 — render the presskit from data.xml with the stdlib renderer.
# No Node, no sharp: the old presskit.html toolchain no longer builds.
FROM python:3.12-slim AS press
WORKDIR /src
COPY . .
RUN python3 render_press.py && test -f build/press/index.html

# Stage 2 — static server. / is the studio & shuttle landing; /press is the presskit.
FROM caddy:2-alpine
COPY landing-index.html /srv/index.html
COPY --from=press /src/build/press /srv/press
COPY Caddyfile /etc/caddy/Caddyfile

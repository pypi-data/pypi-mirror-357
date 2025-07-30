# TODO
## mcpgateway cli
- [ ] Add stop to `mcpgateway` to kill / stop all processes
- [ ] Issue stopping mcpgateway using ^C (it waits for network connections to stop)

## Translate
- [ ] Add translate to mcpgateway cli

## Docs: README
- [ ]`- -v $(pwd)/data:/app` - this needs /app/db/...
- [ ] Add docs for `--host` and describe macos issues

## Testing
- [ ] Seession management across multiple containers (have 3 containers, kill the one that I'm connected to, see what happens) - does the session state complete?

## Benchmark
- Compare with other gateways
- e2e benchmark vs. raw mcp servers
- create a few very fast time servers in go or rust..

# Shadowrocket Configuration

A single-file Shadowrocket routing configuration. The importable profile is [`shadowrocket.conf`](shadowrocket.conf).

**Subscribe:** `https://raw.githubusercontent.com/roseshot/Shadowrocket-config/main/shadowrocket.conf`

## Getting started

1. Configure your own proxy nodes in Shadowrocket. This repository does not contain credentials or subscriptions.
2. Import the profile and select **Configuration** routing mode.
3. Review the routing, DNS, and TLS interception settings before enabling them. Install and explicitly trust the local CA only if you intend to use HTTPS inspection.
4. Verify routing and DNS behavior with Shadowrocket connection logs and device-side tests.

The profile contains static `DIRECT`, `PROXY`, and `REJECT-DROP` rules, a generated domain-acceleration section, and HTTPS inspection exclusions. It references HaGeZi Multi LIGHT and Encrypted DNS Only as its runtime external rule lists.

**Limitations:** The profile is large (more than 100,000 static rules); actual device support and performance must be tested. Wide domain and IP rules can block legitimate services. `DIRECT` exposes the device's network address to the destination. TLS inspection can break apps using certificate pinning.

## Development

**Runtime:** Python 3.15. To check the profile's format locally:

```bash
python scripts/check_conf_format.py shadowrocket.conf
```

The format checker validates the required sections and directive shapes, but does not test routing on an actual device. Domain synchronization and registration auditing remain in the [scheduled workflow](docs/domain-audit.md).

## Documentation

See the [documentation index](docs/README.md) for operations and rule-source evidence.

## License

See [LICENSE](LICENSE).

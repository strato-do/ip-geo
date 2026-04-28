# ip-geo

A high-accuracy IPv4 / IPv6 geolocation database in MaxMind DB format,
with city-level precision. Rebuilt weekly.

## Download

[Latest release](https://github.com/strato-do/ip-geo/releases/latest) —
`ip-geo.mmdb` and `SHA256SUMS`.

## Usage

```bash
pip install maxminddb
```

```python
from lookup import open_database

with open_database("ip-geo.mmdb") as reader:
    print(reader.lookup("216.24.60.0"))
```

## Output

```json
{
  "ip": "216.24.60.0",
  "country_code": "US",
  "country_name": "United States",
  "registered_country_code": "US",
  "registered_country_name": "United States",
  "continent_code": "NA",
  "continent_name": "North America",
  "region": "California",
  "region_code": "CA",
  "city": "San Francisco",
  "latitude": 37.77493,
  "longitude": -122.41942,
  "postal_code": "94107",
  "timezone": "America/Los_Angeles",
  "asn": {
    "number": 14618,
    "name": "Amazon.com, Inc.",
    "domain": "amazon.com"
  }
}
```

The shape is stable per IP — unresolved fields are `null`, never omitted.

## License

[MIT](LICENSE).

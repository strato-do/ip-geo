#!/usr/bin/env python3
"""Self-contained reader for ip-geo.mmdb.

Records are stored in a packed layout for size. This helper expands them
back to the documented JSON schema with a stable null shape.
"""
from __future__ import annotations

import argparse
import ipaddress
import json
import sys

import maxminddb


_TOP_LEVEL_FIELDS = (
    "country_code",
    "country_name",
    "registered_country_code",
    "registered_country_name",
    "continent_code",
    "continent_name",
    "region",
    "region_code",
    "city",
    "latitude",
    "longitude",
    "postal_code",
    "timezone",
)
_ASN_FIELDS = ("number", "name", "domain")


def _null_record():
    return {
        **{f: None for f in _TOP_LEVEL_FIELDS},
        "asn": {f: None for f in _ASN_FIELDS},
    }


def _unpack(record):
    if not record:
        return _null_record()
    if isinstance(record, dict):
        out = _null_record()
        for k, v in record.items():
            if k == "asn" and isinstance(v, dict):
                out["asn"] = {**out["asn"], **v}
            else:
                out[k] = v
        return out
    mask = int(record[0])
    values = iter(record[1:])
    out = _null_record()
    bit = 0
    for field in _TOP_LEVEL_FIELDS:
        if mask & (1 << bit):
            out[field] = next(values)
        bit += 1
    for field in _ASN_FIELDS:
        if mask & (1 << bit):
            out["asn"][field] = next(values)
        bit += 1
    return out


def _normalize_ip(ip):
    addr = ipaddress.ip_address(str(ip).strip())
    mapped = getattr(addr, "ipv4_mapped", None)
    if mapped is not None:
        addr = mapped
    return str(addr)


class Reader:
    def __init__(self, path):
        self._reader = maxminddb.open_database(path)

    def lookup(self, ip):
        normalized = _normalize_ip(ip)
        return {"ip": normalized, **_unpack(self._reader.get(normalized))}

    def close(self):
        self._reader.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


def open_database(path):
    return Reader(path)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Lookup IPs in ip-geo.mmdb.")
    ap.add_argument("ip", nargs="+")
    ap.add_argument("--db", default="ip-geo.mmdb")
    ap.add_argument("--pretty", action="store_true")
    args = ap.parse_args(argv)

    with open_database(args.db) as reader:
        results = [reader.lookup(ip) for ip in args.ip]

    out = results[0] if len(results) == 1 else results
    kwargs = {"ensure_ascii": False}
    if args.pretty:
        kwargs.update({"indent": 2, "sort_keys": True})
    print(json.dumps(out, **kwargs))


if __name__ == "__main__":
    sys.exit(main() or 0)

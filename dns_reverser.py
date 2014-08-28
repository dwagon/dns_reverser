#!/usr/bin/env python

import sys
import re


###############################################################################
def parse_zone(fname):
    ipaddrs = {}
    zone = None
    with open(fname) as fh:
        for line in fh:
            if not line.strip():
                continue
            if line.startswith(';'):
                continue
            # ORIGIN
            m = re.search('\$ORIGIN\s+(?P<domain>\S+)', line)
            if m:
                zone = m.groupdict()['domain']
                continue
            # SOA records
            m = re.search('(?P<domain>\S+)\s+IN\s+SOA\s+', line)
            if m:
                zone = m.groupdict()['domain']
                continue
            # NS records
            m = re.search('(?P<hostname>\S+)?\s+IN\s+NS\s+(?P<cname>\S+)', line)
            if m:
                continue
            # CNAME records
            m = re.search('(?P<hostname>\S+)\s+IN\s+CNAME\s+(?P<cname>\S+)', line)
            if m:
                continue
            # A records
            m = re.search('(?P<hostname>\S+)\s+IN\s+A\s+(?P<ip>\d+\.\d+\.\d+\.\d+)', line)
            if m:
                hostname = m.groupdict()['hostname']
                ip = m.groupdict()['ip']
                if not hostname.endswith('.'):
                    hostname = "%s.%s" % (hostname, zone)
                if ip in ipaddrs:
                    ipaddrs[ip].add(hostname)
                else:
                    ipaddrs[ip] = set([hostname])
                continue
            print "Unhandled line: %s" % line.strip()
    return ipaddrs


###############################################################################
def generate_reverse(ipmap):
    revzones = {}
    for k, v in ipmap.items():
        a, b, c, d = k.split('.')
        net = "%s.%s.%s" % (a, b, c)
        if net not in revzones:
            revzones[net] = {}
        revzones[net][d] = v

    for k in revzones.keys():
        a, b, c = k.split('.')
        with open('%s.%s.%s.in-addr.arpa' % (c, b, a), 'w') as fh:
            for v in sorted(revzones[k], key=int):
                if len(revzones[k][v]) > 1:
                    fh.write("; %s\tIN PTR %s ; PICK ONE\n" % (v, " ".join(list(revzones[k][v]))))
                else:
                    fh.write("%s\tIN PTR %s\n" % (v, list(revzones[k][v])[0]))


###############################################################################
def main():
    fname = sys.argv[1]         # TODO: argparse

    ipmap = parse_zone(fname)
    generate_reverse(ipmap)


###############################################################################
if __name__ == "__main__":
    main()

# EOF

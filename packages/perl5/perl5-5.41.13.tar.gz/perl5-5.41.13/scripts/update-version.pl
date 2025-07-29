#!/usr/bin/env -S perl -pi
BEGIN {
    exit if scalar @ARGV == 0;
    $version =
`curl -s https://api.github.com/repos/Perl/perl5/releases/latest | jq -r .tag_name`;
    chomp $version;
    $version =~ s/^v//;
}

s/(?<=version = ")[^"]+/$version/;

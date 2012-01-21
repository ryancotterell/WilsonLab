#!/usr/bin/perl

use strict;
use utf8;

my $input = $ARGV[0];
binmode(STDOUT, ":utf8");
open FILE, "<:utf8", $input or die $!;

my @set1;
my @set2;

while (<FILE>) {
    my @data = split(/\t\t/, $_);
    
    if ($data[2] =~ m/^(d|t).*/g || $data[2] =~ m/(d|t)$/g) {
	push(@set1, $data[2]);
    }
    else {
	push(@set2, $data[2]);
    }
}

print @set1;
print;
print;
print;
print @set2;

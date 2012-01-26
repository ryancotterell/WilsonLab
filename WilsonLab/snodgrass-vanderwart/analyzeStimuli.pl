#!/usr/bin/perl

use strict;
use utf8;

my $input = $ARGV[0];
binmode(STDOUT, ":utf8");
open FILE, "<:utf8", $input or die $!;

my @set1;
my @set2;

my $count1 = 0;
my $count2 = 0;

while (<FILE>) {
    my @data = split(/\t\t/, $_);
    
    if ($data[2] =~ m/^(p|t|k).*/g) {
	push(@set1, $data[2]);
	$count1++;
    }
    else {
	push(@set2, $data[2]);
	$count2++;
    }
}

#print @set1;
#print $count1, "\n";
print;
print;
print;
print @set2;
print $count2, "\n";

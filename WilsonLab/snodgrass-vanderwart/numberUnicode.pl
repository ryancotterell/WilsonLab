#!/usr/bin/perl

use strict;
use utf8;
use Encode::Escape;
use WWW::Mechanize;

binmode(STDOUT, ":utf8");

my $file1 = $ARGV[0];
my $file2 = $ARGV[1];

open FILE1, $file1 or die $!;
open FILE2, ">>:utf8", $file2 or die $!;

my $count = 1;
while(<FILE1>) {
    chomp $_;
    $_ = lc $_;
    my $num = sprintf "%03d\t\t", $count;
    print $num;
    my $string = getIPA($_);
    $string =~ s/\n//g;
    syswrite FILE2, "$num$_\t\t$string\n";
    $count++;
}


sub getIPA() {
    my $mech = WWW::Mechanize->new();
    my $url = "http://upodn.com/";

    my $input = lc shift @_;
    $input .= ' ' . lc $_ for(@_);
    if ($input ne '') {
	chomp $input;
	$mech->get($url);
	$mech->field('intext', $input);
	$mech->submit();

	my $content = $mech->content();
	$content =~ m/(<table.*>)(.*)<\/font>/g;
	my $word = $2;
	$word =~ s/^\s*//;
	$word =~ s/\s$//;
	$word =~ s/&#x(\S\S\S\S);/\\x{$1}/g;
	$word = decode 'unicode-escape', $word;
	$word =~ s/tʃ/ʧ/g;
	$word =~ s/dʒ/ʤ/g;

	return $word;
    }
}

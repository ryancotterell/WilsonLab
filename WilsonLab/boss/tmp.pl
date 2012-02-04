#!/usr/bin/perl
use strict;
use WWW::Mechanize::Firefox;
    
my %imageurls;

my $url ="http://boss.smugmug.com/Other/480-normalized-photos/9484560_B6pGVC#!i=888830522&k=ABLqx";
my $mech = WWW::Mechanize::Firefox->new();
$mech->get($url);
print $url, "\n";
$imageurls{$url} = 1;
my $count = 1;

while ($count < 480) {
    my @links = $mech->selector('a');
    $mech->highlight_node(@links);

    for my $link (@links) {
#	print $link->{href}, "\n";
	if ((length $link->{href} == 87)) {
	    if (!exists $imageurls{$link->{href}}) {
		$url = $link->{href};
		print $url, "\n";
		$imageurls{$url} = 1;
		$count++;
		last;
	    }
	}
    }
    $mech->get($url);
}

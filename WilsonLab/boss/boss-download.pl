#!/usr/bin/perl

use strict;
use WWW::Mechanize::Firefox;

my $mech = WWW::Mechanize::Firefox->new();

my $url = "http://boss.smugmug.com/Other/480-normalized-photos/9484560_B6pGVC#!p=1&n=10";

$mech->get($url);

#while(1) {
#    $mech->content =~ m#src="(.*)" itemprop="contentURL"#g;
#    print $1, "\n";
#    my $link = $mech->find_link(text=>'2');
 #   $url = $link->url();
  #  print $url, "\n";
 #   $mech->get($url);
#}


for my $tmp ($mech->links) {
    print $tmp->text(), "\n";
}

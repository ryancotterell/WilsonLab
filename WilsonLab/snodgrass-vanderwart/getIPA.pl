#!/usr/bin/perl
#Returns the unicode output of a string entered through the 
#command line. Scrapes the unicode equivalent at upodn.com
#Ryan Cotterell
#2012
use utf8;
use Encode::Escape;
use WWW::Mechanize;

$mech = WWW::Mechanize->new();
$url = "http://upodn.com/";

$input = shift @ARGV;
$input .= ' ' . $_ for(@ARGV);
if ($input eq '') {
    print "A string argument is required";
}
else {

    $mech->get($url);
    $mech->field('intext', $input);
    $mech->submit();

    binmode(STDOUT, ":utf8");
    $content = $mech->content();
    $content =~ m/(<table.*>)(.*)<\/font>/g;
    $word = $2;
    $word =~ s/^\s*//;
    $word =~ s/\s$//;
    $word =~ s/&#x(\S\S\S\S);/\\x{$1}/g;
    $word = decode 'unicode-escape', $word;

    if ($word eq '') {
	print "Word not found";
    }
    else {
	print $word;
    }
}

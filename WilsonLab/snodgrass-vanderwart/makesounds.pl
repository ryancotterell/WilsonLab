#!/usr/bin/perl

open FILE, names;

my $count = 0;
while(<FILE>) {
    chomp $_;
    my $text = "click on the " . (lc $_);
    $count++;
    $num = sprintf("%03d", $count);
    my $filename = $num . ".wav";
    system ("espeak -p 90 -v mb-us1 -w $filename \"$text\"");
}

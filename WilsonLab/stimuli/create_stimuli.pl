#!/usr/bin/perl
 
use strict;
use Algorithm::Permute;
use List::Util qw (shuffle);

open FILE, "stimuli" or die $!;
my $num_stims = 120;

my @conditionA;
my @conditionB;
my @other;

my %conditionAWords;
my %conditionBWords;
my %otherWords;

my $count = 0;

while (<FILE>) {
    chomp $_;
    $_ =~ m/(.*)\t\t(.*)\t\t(.*)/g;
    if ($count < $num_stims / 4) {
	push(@conditionA, $1);
	$conditionAWords{$1} = $2;
    }
    elsif ($count < $num_stims / 2) {
	push(@conditionB, $1);
	$conditionBWords{$1} = $2;
    }
    else {
	push(@other, $1);
	$otherWords{$1} = $2;
    }
    $count++;
}

@conditionA = shuffle @conditionA;
@conditionB = shuffle @conditionB;
@other = shuffle @other;

open WORDSFILE, ">", "files_in_words";
open FILE, ">", "files";
for (1..($num_stims / 4)) {
    my $conditionA = pop(@conditionA);
    my $conditionB = pop(@conditionB);
    my $other1 = pop(@other);
    my $other2 = pop(@other);

    print WORDSFILE $conditionAWords{$conditionA}, "\t\t", $conditionBWords{$conditionB}, "\t\t", 
    $otherWords{$other1}, "\t\t", $otherWords{$other2};
    print WORDSFILE "\n";

    print FILE $conditionA . ".png, " . $conditionB . ".png, " . $other1 . ".png, " . $other2 . ".png, " . $conditionA . ".wav\n";

}

#!/usr/bin/perl

 open(FILE,  ">>", "output.txt") 
	or die "cannot open > output.txt: $!";

print FILE "Hello";

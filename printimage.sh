#!/bin/bash
set -x
LF="\n" # 0x0a
CR="\x0d"
FF="\x0c"
ESC="\x1b"
GS="\x1d"
HT="\t" # 0x09
printerInitializeCommand="${ESC}@"
startPageCommand="${ESC}2"
endPageCommand="$FF"
endJobCommand="${GS}""r1"
PageCutCommand="${ESC}""i"
BuzzerCommand="${ESC}""\x1e"


invert="$GS""B\x01"
uninvert="$GS""B\x00"

function invert {
    echo -ne "$GS""B\x01""$1""${GS}B\x00"
}
function jobsetup {
    echo -ne $printerInitializeCommand
}
function pagesetup {
    echo -ne $startPageCommand
}
function endPage {
    echo -ne $endPageCommand
    echo -ne "\n\n\n\n"$PageCutCommand
}
function endJob {
    echo -ne $endJobCommand
    echo -ne "\n\n\n\n"$PageCutCommand
}
function hexwidth {
    echo  `perl -e '$a='$1' / 8; printf "\\\\x%02x\\\\x%02x",  ($a - ($a >> 8 << 8)), $a >> 8;'`
}
function hexheight {
    echo  `perl -e '$a='$1'; printf "\\\\x%02x\\\\x%02x",  ($a - ($a >> 8 << 8)), $a >> 8;'`
}
function header {
    convert "$1" -resize 640x1024\> pbm:- | grep -av ^\# | head -2
}
function getwidth {
    echo $@ | xargs | awk '{print $2}'
}
function getheight {
    echo $@ | xargs | awk '{print $3}'
}

function main {
    jobsetup;
    pagesetup;
    pbmheader=`header "$1"`
    # rasterheader
    echo -ne "${GS}v00"
#    echo -ne "\x50\x00" # 640 pixels wide (640/8)
    wid=`getwidth $pbmheader`
    hei=`getheight $pbmheader`
    echo -ne `hexwidth $wid` # width
    echo -ne `hexheight $hei` # height
    convert "$1" -resize 640x1024\> pbm:- | dd bs=`echo -ne $pbmheader | wc -c` skip=1
    echo -ne $endPageCommand
    endJob

}
main "$1"

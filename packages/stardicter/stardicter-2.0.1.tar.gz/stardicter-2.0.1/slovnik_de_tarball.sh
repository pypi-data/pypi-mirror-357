#!/bin/sh
#
# Script to create tarballs of GNU/FDL Anglicko-Český slovník
#
# Copyright (c) 2006 - 2017 Michal Čihař
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see http://www.gnu.org/licenses/.

set -e

if [ "x$1" = 'x--wrap' ] ; then
    WRAP="$2"
    shift 2
fi

NAME=stardict-german-czech
dir="$NAME-`date +%Y%m%d`"
dira="$dir-ascii"
diran="$dir-ascii-notags"
dirn="$dir-notags"
dirs="$dir-source"

rm -rf $dir
mkdir $dir

$WRAP ./sdgen.py --all --change --write-source --directory $dir "$@" czechgerman

if [ ! -f $dir/README ] ; then
    rm -rf $dir
    exit 0
fi

# Compress
dictzip $dir/*.dict

# Split to separate dirs
rm -rf $dira $dirn $diran $dirs
mkdir $dira
mkdir $dirn
mkdir $diran
mkdir $dirs

cp $dir/README $dira/
cp $dir/README $dirn/
cp $dir/README $diran/
cp $dir/README $dirs/

mv $dir/*-ascii-notags* $diran/
mv $dir/*-ascii* $dira/
mv $dir/*-notags* $dirn/
mv $dir/de-cs.txt $dirs/

# Create tarballs
tar --owner=root --group=root --numeric-owner -czf $dir.tar.gz $dir
tar --owner=root --group=root --numeric-owner -czf $dira.tar.gz $dira
tar --owner=root --group=root --numeric-owner -czf $dirn.tar.gz $dirn
tar --owner=root --group=root --numeric-owner -czf $diran.tar.gz $diran
tar --owner=root --group=root --numeric-owner -czf $dirs.tar.gz $dirs
rm -rf $dir $dira $dirn $diran $dirs

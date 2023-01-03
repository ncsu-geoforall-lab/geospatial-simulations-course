#!/bin/bash

# builds pages from source

function build_page {
    FILE_SOURCE=$1
    FILE_TARGET=$2
    cat $HEAD_FILE > $OUTDIR/$FILE_TARGET
    echo "<!-- This is a generated file. Do not edit. -->" >> $OUTDIR/$FILE_TARGET
    cat $FILE_SOURCE >> $OUTDIR/$FILE_TARGET
    cat $FOOT_FILE >> $OUTDIR/$FILE_TARGET
}

HEAD_FILE=`pwd`/head.html
FOOT_FILE=`pwd`/foot.html

OUTDIR="build"

if [ ! -d "$OUTDIR" ]; then
    mkdir $OUTDIR
    echo "Creating directory $OUTDIR automatically."
fi

# disable Jekyll which is not needed for out GitHub pages
touch $OUTDIR/.nojekyll

if [ ! -d "$OUTDIR" ]; then
    echo "The directory $OUTDIR does not exists and it will be created for you."
    mkdir $OUTDIR
fi

for FILE in `ls *.html|grep -v foot|grep -v head`
do
    build_page $FILE $FILE
done

for FILE in *.css
do
    cp $FILE $OUTDIR
done

for DIR in img
do
    cp -r $DIR $OUTDIR
done

for DIR in topics assignments
do
    mkdir -p $OUTDIR/$DIR

    for FILE in `ls $DIR/*.html`
    do
        TGT_FILE=$OUTDIR/$DIR/`basename $FILE`
        ./increase-link-depth.py < $HEAD_FILE > $TGT_FILE
        echo "<!-- This is a generated file. Do not edit. -->" >> $TGT_FILE
        ./edit.py < $FILE >> $TGT_FILE
        ./increase-link-depth.py < $FOOT_FILE >> $TGT_FILE
    done

    for SUBDIR in data img
    do
        # copy only if directory exists
        if [ -d "$DIR/$SUBDIR" ]; then
            cp -r $DIR/$SUBDIR $OUTDIR/$DIR
        fi
    done
done

for DIR in resources
do
    mkdir -p $OUTDIR/$DIR

    # Copy all files with name and extension naming scheme.
    # (Ignore anything which looks special, e.g., directories.)
    for FILE in `ls $DIR/*.*`
    do
        cp $FILE $OUTDIR/$DIR
    done

    for SUBDIR in `ls $DIR/*`
    do
        if [ -d "$DIR/$SUBDIR" ]; then
            cp -r $DIR/$SUBDIR $OUTDIR/$DIR
        fi
    done
done

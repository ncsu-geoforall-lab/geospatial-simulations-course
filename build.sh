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

function build_page_rst {
    FILE_SOURCE=$1
    FILE_TARGET=$2
    cat $HEAD_FILE > $OUTDIR/$FILE_TARGET
    echo "<!-- This is a generated file. Do not edit. -->" >> $OUTDIR/$FILE_TARGET
    pandoc --to=html $FILE_SOURCE >> $OUTDIR/$FILE_TARGET
    cat $FOOT_FILE >> $OUTDIR/$FILE_TARGET
}

function build_page_rst_subdir {
    FILE_SOURCE=$1
    FILE_TARGET=$2
    ./increase-link-depth.py < $HEAD_FILE > $OUTDIR/$FILE_TARGET
    echo "<!-- This is a generated file. Do not edit. -->" >> $OUTDIR/$FILE_TARGET
    pandoc --to=html $FILE_SOURCE >> $OUTDIR/$FILE_TARGET
    ./increase-link-depth.py < $FOOT_FILE >> $OUTDIR/$FILE_TARGET
}

HEAD_FILE=`pwd`/head.html
FOOT_FILE=`pwd`/foot.html

OUTDIR="build"

if [ ! -d "$OUTDIR" ]; then
    mkdir $OUTDIR
    echo "Creating directory $OUTDIR automatically."
    echo "If you are using GitHub pages to create publish the website,"
    echo "you probably want to create this directory by a dedicated script."
fi

# disable Jekyll which is not needed for out GitHub pages
touch $OUTDIR/.nojekyll

if [ ! -d "$OUTDIR" ]; then
    echo "The directory $OUTDIR does not exists and it will be created for you."
    mkdir $OUTDIR
fi

for FILE in `ls *.rst|grep -v foot|grep -v head`
do
    build_page_rst $FILE `basename -s .rst $FILE`.html
done

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

for DIR in topics
do
    mkdir -p $OUTDIR/$DIR

    for FILE in `ls $DIR/*.rst|grep -v foot|grep -v head`
    do
        build_page_rst_subdir $FILE $DIR/`basename -s .rst $FILE`.html
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

    for FILE in `ls $DIR/*.html $DIR/*.geojson $DIR/*.png`
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

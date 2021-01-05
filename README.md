Geospatial Computing and Simulations
====================================

This is a repository for a course website and teaching materials.

For reference about the template the website style see:

- <https://github.com/ncsu-geoforall-lab/course-website-template>
- <https://github.com/ncsu-geoforall-lab/geospatial-modeling-course>

To learn about Git and GitHub, you can use:

- <http://ncsu-geoforall-lab.github.io/git-and-github-workshop/>

Requirements
------------

- Bash
- Python
- Pandoc when using rst files

Build and publish
-----------------

The pages are build from the source code and placed into a separate
directory. Web page is published using GitHub pages. The publishing step
is done automatically.

### Building the pages

In your clone of the repository where you are in master branch, use
`build.sh` script to build the pages.

    ./build.sh

The directory where pages are build is inside the directory with the
source code and is named `build`. You can look at the pages using e.g.:

    firefox build/index.html

If you don\'t see the changes you have made, delete the file in the
build directory and build again (the mechanism to recognize changes is
not smart).

To build lectures go to the lecture directory and run the `build.sh` for
lectures script there, i.e.:

    cd lectures
    ./build.sh

It is important to always be in the directory where the `build.sh`
script is for each part.

### Publishing the pages

Once the changed and committed and pushed to the master branch, the
website will be deployed automatically using GitHub Actions.

Authors
-------

Copyright 2018 by

- Helena Mitasova, NCSU GeoForAll
- Vaclav Petras, NCSU GeoForAll
- Anna Petrasova, NCSU GeoForAll

Course developed at North Carolina State University.

License and use
---------------

The course material is under CC BY-SA 4.0 license.

<https://creativecommons.org/licenses/by-sa/4.0/>

For the website style see:

<https://github.com/ncsu-geoforall-lab/course-website-template>

For information on lecture slides (presentations) see:

<https://github.com/ncsu-geoforall-lab/lecture-slides-template>

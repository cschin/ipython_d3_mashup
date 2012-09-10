=================================================================================
Using pythonbrew to install minimum scientific computing environment on OS X 10.8
=================================================================================


Here is a list of packages that we want to install::

    $ pip freeze
    distribute==0.6.28
    h5py==2.0.1
    ipython==0.13
    matplotlib==1.1.1
    numpy==1.6.2
    pyzmq==2.2.0.1
    scipy==0.10.1
    tornado==2.4
    wsgiref==0.1.2


First Step: Install Xcode and ``gfortran``
==========================================

First, you have should have Xcode 4.4.1 installed so you can compile some ``C``
program.  

You will need the "command line tools" from Xcode 4.4.1.  A version of such
tool can be downloaded from https://developer.apple.com/downloads/index.action
(an Apple ID is needed), or using Xcode 4.4.1 through the "Download Pane" in
the preference setting to download and install it.  You will also need some
``Fortran`` complier to install ``scipy`` too.

There are various ways to install the fortran compiler with OS X 10.8 as shown in
this page http://hpc.sourceforge.net. Among the different ways to
install Fortran, the easiest one is to download ``gcc-mlion.tar.gz``
(http://prdownloads.sourceforge.net/hpc/gcc-mlion.tar.gz) and directly un-tar it
to install gcc 4.8 + gfortran in to ``/usr/local/``.  However, this might cause
some problem as the package does include the ``gcc`` 4.8 compiler which may
cause some confliction with the Xcode's gcc compiler. Here is the order
of directory for binary lookup in my ``PATH`` environment variable::

    /usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin:/Applications/Xcode.app/Contents/Developer/usr/bin/

It will allow to use the ``gcc`` from Xcode and ``gfortran`` from ``/usr/local/bin``.

Install pythonbrew
==================

One can find the installation guide for pythonbrew here
https://github.com/utahta/pythonbrew

The installation on OS X 10.8 is straight forward. We just need to follow the
instruction from the pythonbrew's github page. Open a terminal and use the
following command::

    $ curl -kL http://xrl.us/pythonbrewinstall | bash

If you don't want to invoke pythobrew automatically, you don't need add this
line to the ``.bashrc``::

    [[ -s "$HOME/.pythonbrew/etc/bashrc" ]] && source "$HOME/.pythonbrew/etc/bashrc"

Instead, you can load the pythonbrew environment within ``bash`` by::

    $ source "$HOME/.pythonbrew/etc/bashrc"

to invoke pythobrew manually. This is my preferred way to make sure I am aware
what environment I am using.

Now, install ``python`` 2.7.2::
    
    $ pythonbrew install 2.7.2

At this stage, you can use the ``pythonbrew``'s python by asking pythonbrew to
setup the environment for you::

    $ pythonbrew use Python-2.7.2

You have a clean environment now. You can check the python package installed by::

    $ pip freeze
    distribute==0.6.28
    wsgiref==0.1.2


Install ``numpy``
===========================

There is a potential bug in ``pip`` such that the direct commend ``pip install
numpy`` might not install everything that we need for installing ``scipy``. If
you install ``numpy`` by::

    $ pip install numpy

It will miss a configuration file (``npymath.ini``) that is needed for
compiling ``scipy``.  Instead, we can download the ``numpy`` source using
``pip``::

    $ pip install  numpy -d work_dir
    $ cd work_dir
    $ unzip numpy-numpy-1.6.2.zip

then install ``numpy`` with ``setup.py``::

    $ cd numpy-numpy-1.6.2
    $ python setup.py install

You should check if ``npymath.ini`` exists::

    $ cat /Users/username/.pythonbrew/pythons/Python-2.7.2/lib/python2.7/site-packages/numpy/core/lib/npy-pkg-config/npymath.ini
    [meta]
    Name=npymath
    Description=Portable, core math library implementing C99 standard
    Version=0.1

    [variables]
    pkgname=numpy.core
    prefix=${pkgdir}
    libdir=${prefix}/lib
    includedir=${prefix}/include

    [default]
    Libs=-L${libdir} -lnpymath
    Cflags=-I${includedir}
    Requires=mlib

    [msvc]
    Libs=/LIBPATH:${libdir} npymath.lib
    Cflags=/INCLUDE:${includedir}
    Requires=mlib


Install ``scipy``
===========================

Similarly, it is better to download the source of ``scipy`` to install it with ``setup.py``::

    $ pip install scipy -d work_dir
    $ cd work_dir
    $ unzip scipy-0.10.1.zip
    $ cd scipy-0.10.1

However, due to the ``C`` header changes in OS X 10.8, we will need to modify a 
number of lines of the ``C`` source code in ``scipy`` to be able to compile it under
10.8. This is the kind of errors that one will encounter if we use ``python setup.py`` to install
``scipy``::

    /System/Library/Frameworks/vecLib.framework/Headers/vecLib.h:22:4: error: #error "<vecLib/vecLib.h> is deprecated.  Please #include <Accelerate/Accelerate.h> and link to Accelerate.framework."

One way to bypass such error is the set the ``__ACCELERATE__`` compiler flag::

    $ export CFLAGS=-D__ACCELERATE__

Once the flag is set, use ``setup.py`` to install scipy::

    $ cd work_dir/scipy
    $ python setup.py install

At this stage, you should have $numpy$ and $scipy$ installed::

    $ pip freeze
    distribute==0.6.28
    numpy==1.6.2
    scipy==0.10.1
    wsgiref==0.1.2



Install ``libhdf5``
===========================

Download ``libhdf5`` from http://www.hdfgroup.org/ftp/HDF5/current/src/, un-tar the
downloaded ``hdf5-1.8.9.tar.bz2``::

    $ tar jxvf hdf5-1.8.9.tar.bz2

Configure and build ``libhdf5``:

    $ cd hdf5-1.8.9
    $ ./configure --prefix=$HOME/.pythonbrew/
    $ make
    $ make install


Install ``h5py``
============================

Download ``h5py`` use ``pip``::

    $ pip install h5py -d work_dir
    $ cd work_dir
    $ tar zxvf h5py-2.0.1.tar.gz 
    $ cd zxvf h5py-2.0.1

Install ``h5py``, the only thing one need to worry about is to tell ``setup.py`` where
the ``libhdf5``'s root directory is.::

    $ python setup.py build --hdf5=$HOME/.pythonbrew
    $ python setup.py install


Install ``IPython``
=====================

We need ``tornado`` and ``pyzmq`` so the cool ``ipythno notebook`` can work::

    $ pip install tornado
    $ pip install pyzmq

Install ``IPython``::
    
    $ pip install ipython

Now, we get these packages::

    $ pip freeze ipython
    distribute==0.6.28
    h5py==2.0.1
    ipython==0.13
    numpy==1.6.2
    pyzmq==2.2.0.1
    scipy==0.10.1
    tornado==2.4
    wsgiref==0.1.2


Install ``matplotlib``
============================

prerequisites: freetype2 and libpng

install freetype2::

    $ mv ~/Downloads/freetype-2.4.10.tar.bz2 .
    $ tar jxvf freetype-2.4.10.tar.bz2
    $ cd freetype-2.4.10
    $ ./configure --prefix=$HOME/.pythonbrew/
    $ make install

install libpng::

    $ wget http://ncu.dl.sourceforge.net/project/libpng/libpng15/1.5.12/libpng-1.5.12.tar.gz
    $ tar zxvf libpng-1.5.12.tar.gz
    $ cd ./lpng1512/ 
    $ rm -rf ~/Downloads/lpng1512-1/
    $ cp scripts/makefile.darwin makefile
    $ vi makefile  # change the prefix variable, point it to the $HOME/.pythonbrew directory
    $ make install

install matplotlib::

    $ pip install matplotlib -d work_dir
    $ cd work_dir/
    $ tar zxvf matplotlib-1.1.1.tar.gz
    $ cd matplotlib-1.1.1
    $ python setup.py install


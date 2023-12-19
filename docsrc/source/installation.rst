Installation
-------------
Clone the code from github::

    git clone https://github.com/mpifr-vlbi/dbbc3.git

Do a system wide installation (might require root priviliges)::

    cd dbbc3/lib
    python setup.py install

Alternatively you can do a local installation (current user only)::

    python setup.py install --user

Note: This will only install the dbbc3 package. The standalone utilities and scripts located in the utilities subdirectory must be
manually copied to the target location by the user.

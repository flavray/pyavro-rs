# pyavro_rs



## Installation

The installation currently requires [`cargo`](https://doc.rust-lang.org/cargo/)
to be installed (this will change in the future!)

Here are the steps to follow in order to run the `example` code within a
virtualenv:

    # Install rustup - https://www.rust-lang.org/en-US/install.html
    $ curl https://sh.rustup.rs -sSf | sh

    # Clone pyavro_rs, with the avro-rs-ffi submodule
    $ git clone --recursive https://github.com/flavray/pyavro-rs.git

    $ cd pyavro_rs/examples/
    $ virtualenv virtualenv_run/
    $ source virtualenv_run/bin/activate

    # Install pyavro_rs
    $ pip install -e ..

    $ python example.py

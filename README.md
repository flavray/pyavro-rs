# pyavro-rs

[![GitHub version](https://badge.fury.io/gh/flavray%2Fpyavro-rs.svg)](https://badge.fury.io/gh/flavray%2Fpyavro-rs)
[![Build Status](https://travis-ci.org/flavray/pyavro-rs.svg?branch=master)](https://travis-ci.org/flavray/pyavro-rs)
[![MIT licensed](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/flavray/pyavro-rs/blob/master/LICENSE)

Python wrapper for the [avro-rs](https://github.com/flavray/avro-rs) library. It relies on the official C bindings ([avro-rs-ffi](https://github.com/flavray/avro-rs-ffi)).

This library can be used both directly from native C programs or interfaced with your favorite language to offload encoding and ecoding of [Apache Avro](https://avro.apache.org/) messages.  

For more information on how the original avro-rs works, please have a look at the [documentation](https://docs.rs/avro-rs). 

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

from setuptools import setup, find_packages

def build_native(spec):
    build = spec.add_external_build(
        cmd=['cargo', 'build', '--release'],
        path='./avro-rs-ffi'
    )
    spec.add_cffi_module(
        module_path='pyavro_rs._lowlevel',
        dylib=lambda: build.find_dylib('avro_rs_ffi', in_path='target/release'),
        header_filename=lambda: build.find_header('avro_rs.h', in_path='include'),
        rtld_flags=['NOW', 'NODELETE']
    )

setup(
    name='pyavro_rs',
    packages=find_packages(),
    include_package_data=True,
    setup_requires=['milksnake'],
    install_requires=['milksnake'],
    milksnake_tasks=[build_native],
)

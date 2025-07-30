#!/bin/bash

set -e

# List of packages
packages=( "$@" )

# Loop through each package
for package in "${packages[@]}"
do
    # Check if the tarball exists
    if [ ! -f "$package.tar.gz" ]; then
        echo "Tarball $package.tar.gz not found. Skipping $package."
        echo
        continue
    fi

    echo "Installing $package:"

    # Create a directory for the package
    mkdir -p $package

    # Extract the tarball to the package directory
    tar -xzf $package.tar.gz -C $package --strip-components=1

    # Install the package in very quiet mode by -qq
    pip install ./$package --user --no-deps --no-build-isolation -qq

    # Remove the package directory
    rm -rf $package

    echo "$package installation complete."
    echo
done


# Loop through each package
for package in "${packages[@]}"
do
    # Verify the installation by importing the package
    python -c "import $package; print($package.__file__); print($package.__version__)"

    echo "$package validation complete."
    echo
done

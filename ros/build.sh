# build.sh
# Diego Chavez Arana

#!/usr/bin/env bash

# Get the directory this script resides in
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# nxsdk should be availabe in python path
nxsdk_path=`python3 -c "import nxsdk; print(nxsdk.__path__)"`

pushd $DIR

# Wipe out and re-create the build directory
rm -rf build
mkdir build
cd build

# Copy headers (nxsdkhost.h)
mkdir -p includes/nxsdk
cp -v -R ${nxsdk_path:2:-2}/include includes/nxsdk

# Run CMake/Make
echo "Building Shared Library.............."

cmake ..
make

echo "Shared Library Built................."

popd
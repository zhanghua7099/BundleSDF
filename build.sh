ROOT=$(pwd)
cd /kaolin && pip install -e .
cd ${ROOT}/mycuda && rm -rf build *egg* && pip install -e .
cd ${ROOT}/BundleTrack && rm -rf build && mkdir build && cd build && cmake .. && make -j11
cp /opt/conda/lib/libstdc++.so.6.0.29 /usr/lib/x86_64-linux-gnu/
rm /usr/lib/x86_64-linux-gnu/libstdc++.so.6
ln -s /usr/lib/x86_64-linux-gnu/libstdc++.so.6.0.29 /usr/lib/x86_64-linux-gnu/libstdc++.so.6
pip install PyOpenGL-accelerate

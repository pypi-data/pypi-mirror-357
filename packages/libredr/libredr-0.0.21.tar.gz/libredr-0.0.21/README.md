# LibreDR is an open-source ray-tracing differentiable renderer
[\[Codeberg Repo\]](https://codeberg.org/ybh1998/LibreDR/)
[\[API Document\]](https://ybh1998.codeberg.page/LibreDR/)

LibreDR uses client-server-worker structure to better utilize multiple GPUs (or even multiple nodes on a cluster). \
Some code examples are under the `examples/` directory.

### To run server and worker under Linux:
1. Download `libredr_linux_*.tar.gz` under [\[releases\]](https://codeberg.org/ybh1998/LibreDR/releases).
2. Start server and worker using `examples/scripts/{server,worker}.sh` or with your own configuration. \
Example configurations are in `examples/scripts`. Use `clinfo` to verify OpenCL runtime.

### To run a server and worker under Windows:
1. Download `libredr_windows_*.zip` under [\[releases\]](https://codeberg.org/ybh1998/LibreDR/releases).
2. Start server and worker using `examples/scripts/{server,worker}.bat` or with your own configuration. \
Example configurations are in `examples/scripts`.

### To run the example Python codes or your own Python code
1. Download `libredr-*.whl` under [\[releases\]](https://codeberg.org/ybh1998/LibreDR/releases) and install using
`pip install`, or install from [\[PyPI\]](https://pypi.org/project/libredr/).
2. Run Python example codes `examples/scripts/run_example.{sh,bat}` or your own client codes.

### All the examples are tested on the following platforms:

| Version | OS | Device | Driver | Note |
|---------|----|--------|--------| ---- |
| 🟢v0.0.21 | Debian Bookworm Linux 6.7.12+bpo-amd64 | CPU: Intel Core i7-8550U     | PoCL v3.1                            | Tested on both opencl_program = source and spirv64 |
| 🟢v0.0.21 | Debian Bullseye Linux 6.7.12+bpo-amd64 | GPU: Hygon DCU Z100L         | Hygon Proprietary v25.04             | Tested on opencl_program = source                  |
| 🟢v0.0.21 | Debian Bullseye Linux 6.7.12+bpo-amd64 | GPU: NVIDIA GeForce RTX 3090 | NVIDIA Proprietary v535.216.01       | Tested on opencl_program = source                  |
| 🟢v0.0.21 | Debian Bullseye Linux 6.7.12+bpo-amd64 | GPU: AMD Radeon RX 6700 XT   | AMD ROCm AOMP v19.0-3                | Tested on opencl_program = source                  |
| 🟢v0.0.21 | Debian Bullseye Linux 6.7.12+bpo-amd64 | GPU: Intel UHD Graphics 620  | Intel NEO v22.43.24595.41            | Tested on opencl_program = spir64 and spirv64      |
| 🟢v0.0.21 | Ubuntu 18.04.2 LTS Linux 4.4.179       | GPU: ARM Mali-T860           | ARM Proprietary v1.r14p0-01rel0-git  | Tested on opencl_program = source                  |
| 🟢v0.0.20 | Windows 10 21H2 (OS Build 19044.5608)  | GPU: AMD Radeon RX 6700 XT   | AMD Proprietary v24.12.1             | Unix socket and spir* are not available            |
| 🟢v0.0.20 | Windows 10 21H2 (OS Build 19044.5608)  | GPU: Moore Threads MTT S80   | Moore Threads Proprietary v290.100.1 | Tested on OpenCLOn12 v1.2404.1.0 ⚠️ with performance issue |

To build from source codes for Linux, check the build scripts in `examples/scripts_unix/build/`. Docker is used to
build manylinux-compatible wheels. For Windows, check `examples/scripts_windows/build/`.

Copyright (c) 2022-2025 Bohan Yu. All rights reserved. \
LibreDR is free software licensed under the GNU Affero General Public License, version 3 or any later version.

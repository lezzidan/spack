# Copyright 2013-2023 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)


from spack.package import *


class XsdkExamples(CMakePackage, CudaPackage, ROCmPackage):
    """xSDK Examples show usage of libraries in the xSDK package."""

    homepage = "http://xsdk.info"
    url = "https://github.com/xsdk-project/xsdk-examples/archive/v0.1.0.tar.gz"
    git = "https://github.com/xsdk-project/xsdk-examples"

    maintainers("balay", "luszczek", "balos1", "shuds13", "v-dobrev")

    version("develop", branch="master")
    # FIXME: replace the testing branch with the actual release when available:
    version("0.4.0", branch="testing-v0.4.0")
    version("0.3.0", sha256="e7444a403c0a69eeeb34a4068be4d6f4e5b54cbfd275629019b9236a538a739e")
    version(
        "0.2.0",
        sha256="cf26e3a16a83eba6fb297fb106b0934046f17cf978f96243b44d9d17ad186db6",
        deprecated=True,
    )

    depends_on("xsdk+cuda", when="+cuda")
    for sm_ in CudaPackage.cuda_arch_values:
        depends_on("xsdk+cuda cuda_arch={0}".format(sm_), when="+cuda cuda_arch={0}".format(sm_))
    depends_on("xsdk+rocm", when="+rocm")
    for ac_ in ROCmPackage.amdgpu_targets:
        depends_on("xsdk+rocm amdgpu_target={0}".format(ac_), when="+rocm amdgpu_target={0}".format(ac_))

    depends_on("xsdk@develop", when="@develop")
    depends_on("xsdk@0.8.0", when="@0.4.0")
    depends_on("xsdk@0.8.0 ^mfem+strumpack", when="@0.4.0 ^xsdk+strumpack")
    depends_on("xsdk@0.8.0 ^mfem+ginkgo", when="@0.4.0 ^xsdk+ginkgo")
    depends_on("xsdk@0.8.0 ^mfem+hiop", when="@0.4.0 ^xsdk+hiop")
    depends_on("xsdk@0.8.0 ^mfem+pumi", when="@0.4.0")
    depends_on("xsdk@0.8.0 ^sundials+magma", when="@0.4.0 +cuda")
    depends_on("xsdk@0.7.0", when="@0.3.0")
    depends_on("xsdk@0.7.0 ^mfem+strumpack", when="@0.3.0 ^xsdk+strumpack")
    depends_on("xsdk@0.7.0 ^sundials+magma", when="@0.3.0 +cuda")
    depends_on("xsdk@0.6.0", when="@0.2.0")
    depends_on("mpi")
    depends_on("cmake@3.21:", type="build", when="@0.3.0:")

    def cmake_args(self):
        spec = self.spec

        def enabled(pkg):
            if type(pkg) is not list:
                return "ON" if "^" + pkg in spec else "OFF"
            else:
                return "ON" if all([("^" + p in spec) for p in pkg]) else "OFF"

        # Note: paths to the enabled packages are automatically added by Spack
        # to the variable CMAKE_PREFIX_PATH.
        args = [
            "-DCMAKE_C_COMPILER=%s" % spec["mpi"].mpicc,
            "-DCMAKE_CXX_COMPILER=%s" % spec["mpi"].mpicxx,
            "-DCMAKE_Fortran_COMPILER=%s" % spec["mpi"].mpifc,
            "-DENABLE_AMREX=" + enabled("amrex"),
            "-DENABLE_DEAL_II=" + enabled("dealii"),
            "-DENABLE_GINKGO=" + enabled("ginkgo"),
            "-DENABLE_HEFFTE=" + enabled("heffte"),
            "-DENABLE_HIOP=" + enabled("hiop"),
            "-DENABLE_HYPRE=ON",
            "-DENABLE_MAGMA=" + enabled("magma"),
            "-DENABLE_MFEM=ON",
            "-DENABLE_PETSC=ON",
            # ENABLE_PLASMA also needs Slate:
            "-DENABLE_PLASMA=" + enabled(["plasma", "slate"]),
            "-DENABLE_PRECICE=" + enabled("precice"),
            "-DENABLE_PUMI=ON",
            "-DENABLE_STRUMPACK=" + enabled("strumpack"),
            "-DENABLE_SUNDIALS=ON",
            "-DENABLE_SUPERLU=ON",
            "-DENABLE_TASMANIAN=" + enabled("tasmanian"),
            "-DENABLE_TRILINOS=" + enabled("trilinos"),
        ]

        if "+cuda" in spec["xsdk"]:  # if cuda variant was activated for xsdk
            args.extend(
                [
                    "-DENABLE_CUDA=ON",
                    "-DCMAKE_CUDA_ARCHITECTURES=%s" % spec.variants["cuda_arch"].value,
                ]
            )

        # FIXME: propagate the HIP config from the 'xsdk' package
        if "+rocm" in spec["xsdk"]:  # if rocm variant was activated for xsdk
            args.extend(
                [
                    "-DENABLE_HIP=ON",
                    #"-DCMAKE_CUDA_ARCHITECTURES=%s" % spec.variants["cuda_arch"].value,
                ]
            )

        return args

    def check(self):
        with working_dir(self.build_directory):
            ctest("--output-on-failure")

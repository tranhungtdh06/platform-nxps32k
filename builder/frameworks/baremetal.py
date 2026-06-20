import os
from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()

# Lấy đường dẫn của kho framework tải từ GitHub
FRAMEWORK_DIR = env.PioPlatform().get_package_dir("framework-s32k144-baremetal")

# 1. Tự động nạp thư mục Include
env.Append(
    CPPPATH=[
        os.path.join(FRAMEWORK_DIR, "include")
    ]
)

# 2. Báo cho PlatformIO biết vị trí file Linker (Cách chuẩn, không bị nhân đôi)
env.Replace(
    LDSCRIPT_PATH=os.path.join(FRAMEWORK_DIR, "linker", "S32K144_64_flash.ld")
)

# 3. Tự động biên dịch các file trong thư mục src của framework
env.BuildSources(
    os.path.join("$BUILD_DIR", "FrameworkBaremetal"),
    os.path.join(FRAMEWORK_DIR, "src")
)
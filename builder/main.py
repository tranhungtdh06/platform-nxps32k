import os
import sys
from os.path import join
from SCons.Script import AlwaysBuild, Builder, Default, DefaultEnvironment

env = DefaultEnvironment()
board = env.BoardConfig()

# 1. Cấu hình bộ Toolchain GCC
env.Replace(
    AR="arm-none-eabi-ar",
    AS="arm-none-eabi-as",
    CC="arm-none-eabi-gcc",
    CXX="arm-none-eabi-g++",
    OBJCOPY="arm-none-eabi-objcopy",
    SIZETOOL="arm-none-eabi-size",

    CCFLAGS=[
        "-mcpu=%s" % board.get("build.cpu"),
        "-mthumb",
        "-mfloat-abi=hard",
        "-mfpu=fpv4-sp-d16",
        "-fshort-enums", "-fno-jump-tables", "-funsigned-char",
        "-funsigned-bitfields", "-ffunction-sections", "-fdata-sections",
        "-fno-common", "-O1", "-g"
    ],
    CPPDEFINES=[
        "CPU_S32K144HFT0VLLT",
        "CPU_S32K144",
        "START_FROM_FLASH"
    ],
    LINKFLAGS=[
        "-mcpu=%s" % board.get("build.cpu"),
        "-mthumb",
        "-mfloat-abi=hard",
        "-mfpu=fpv4-sp-d16",
        "-Wl,--gc-sections",
        "-specs=nano.specs", "-specs=nosys.specs"
    ]
)

# 2. Tạo file thực thi
target_elf = env.BuildProgram()
target_hex = env.Alias("firmware.hex", target_elf, env.Command(
    "$TARGET", "$SOURCE", "$OBJCOPY -O ihex $SOURCE $TARGET"
))

# 3. Cấu hình nạp code qua J-Link tự động tải từ PlatformIO
platform = env.PioPlatform()
jlink_dir = platform.get_package_dir("tool-jlink")

# Xác định file chạy dựa trên hệ điều hành (JLink.exe cho Windows, JLinkExe cho Mac/Linux)
uploader_cmd = "JLink.exe" if sys.platform.startswith("win") else "JLinkExe"

# Gắn đường dẫn tuyệt đối nếu tìm thấy gói tool-jlink
if jlink_dir and os.path.isdir(jlink_dir):
    uploader_cmd = join(jlink_dir, uploader_cmd)

env.Replace(
    UPLOADER=uploader_cmd,
    UPLOADERFLAGS=[
        "-device", board.get("debug.jlink_device"), 
        "-if", "SWD", 
        "-speed", "4000", 
        "-autorun", "0", 
        "-CommanderScript", "upload.jlink"
    ],
    UPLOADCMD="$UPLOADER $UPLOADERFLAGS"
)

env.AddPlatformTarget("upload", target_hex, [env.VerboseAction("$UPLOADCMD", "Uploading $SOURCE")], "Upload")

Default([target_elf, target_hex])
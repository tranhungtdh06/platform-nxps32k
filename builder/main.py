import os
import sys
from os.path import join
from SCons.Script import AlwaysBuild, Builder, Default, DefaultEnvironment

env = DefaultEnvironment()
board = env.BoardConfig()

# 1. Ép định dạng tên file chuẩn
env.Replace(PROGNAME="firmware")

# 2. Cấu hình Toolchain
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

# 3. Quá trình biên dịch (Đảm bảo file .hex được tạo ra)
target_elf = env.BuildProgram()
target_hex = env.Command(
    join("$BUILD_DIR", "${PROGNAME}.hex"),
    target_elf,
    "$OBJCOPY -O ihex $SOURCE $TARGET"
)

# 4. Cấu hình Nạp code J-Link
platform = env.PioPlatform()
jlink_dir = platform.get_package_dir("tool-jlink")
uploader_cmd = "JLink.exe" if sys.platform.startswith("win") else "JLinkExe"

if jlink_dir and os.path.isdir(jlink_dir):
    uploader_cmd = join(jlink_dir, uploader_cmd)

# Tự động sinh kịch bản J-Link ẩn bên trong thư mục build
upload_script = join("$BUILD_DIR", "upload.jlink")

def create_jlink_script(target, source, env):
    # Lấy đường dẫn tuyệt đối của file hex
    hex_path = source[0].get_abspath().replace("\\", "/")
    with open(env.subst(upload_script), "w") as f:
        f.write("r\n")
        f.write("loadfile %s\n" % hex_path)
        f.write("r\n")
        f.write("g\n")
        f.write("q\n")

env.Replace(
    UPLOADER=uploader_cmd,
    UPLOADERFLAGS=[
        "-device", board.get("debug.jlink_device"), 
        "-if", "SWD", 
        "-speed", "4000", 
        "-CommanderScript", upload_script
    ],
    UPLOADCMD="$UPLOADER $UPLOADERFLAGS"
)

upload_actions = [
    env.VerboseAction(create_jlink_script, "Generating J-Link script..."),
    env.VerboseAction("$UPLOADCMD", "Uploading firmware...")
]

env.AddPlatformTarget("upload", target_hex, upload_actions, "Upload")

Default([target_elf, target_hex])
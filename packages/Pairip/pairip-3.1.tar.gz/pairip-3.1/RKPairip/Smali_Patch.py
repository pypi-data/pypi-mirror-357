from .C_M import CM; C = CM()
from .Files_Check import FileCheck; F = FileCheck(); F.Set_Path()

# Smali_Patch
def Smali_Patch(smali_folders, CoreX_Hook, isCoreX):
    target_files = ["SignatureCheck.smali", "LicenseClientV3.smali", "LicenseClient.smali", "Application.smali"]
    if CoreX_Hook or isCoreX: target_files.append("VMRunner.smali")

    patterns = []

    if not (isCoreX and not CoreX_Hook):
        patterns.extend([
            (r'invoke-static \{.*\}, Lcom/pairip/SignatureCheck;->verifyIntegrity\(.*?\)V', r'#', "VerifyIntegrity"),
            (r'(\.method (\w+\s+)*verifyIntegrity\(.*?\)V\s+.locals \d+\s+)([\s\S]*?)(return-void\n.end method)', r'\1\4', "VerifyIntegrity"),
            (r'(\.method (\w+\s+)*verifySignatureMatches\(.*?\)Z\s+.locals \d+\s+)([\s\S]*?)(\s+return ([pv]\d+)\n.end method)', r'\1const/4 \5, 0x1\4', "verifySignatureMatches"),
            (r'(\.method (\w+\s+)*connectToLicensingService\(.*?\)V\s+.locals \d+\s+)([\s\S]*?)(return-void\n.end method)', r'\1\4', "connectToLicensingService"),
            (r'(\.method (\w+\s+)*initializeLicenseCheck\(.*?\)V\s+.locals \d+\s+)([\s\S]*?)(return-void\n.end method)', r'\1\4', "initializeLicenseCheck"),
            (r'(\.method (\w+\s+)*processResponse\(.*?\)V\s+.locals \d+\s+)([\s\S]*?)(return-void\n.end method)', r'\1\4', "processResponse")
        ])

    # Custom Device ID
    if CoreX_Hook or isCoreX:
        patterns.append((r'(\.method .*?<clinit>\(\)V\s+.*\n)', r'\1\tconst-string v0, "_Pairip_CoreX"\n\tinvoke-static {v0}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V', f'CoreX_Hook ➸❥ {C.rkj}"lib_Pairip_CoreX.so"'))

    target_file_paths = []
    for smali_folder in smali_folders:
        for root, _, files in C.os.walk(smali_folder):
            for file in files:
                if file in target_files:
                    target_file_paths.append(C.os.path.join(root, file))

    for pattern, replacement, description in patterns:
        for file_path in target_file_paths:
            try:
                if description.startswith("CoreX_Hook") and not file_path.endswith("VMRunner.smali"): continue

                content = open(file_path, 'r', encoding='utf-8', errors='ignore').read()
                new_content = C.re.sub(pattern, replacement, content)
                if new_content != content:
                    print(f"\n{C.lb}[ {C.c}Patch {C.lb}] {C.g}{description} {C.rkj}➸❥ {C.y}{C.os.path.basename(file_path)}")
                    #print(f"\n{C.lb}[ {C.c}Pattern {C.lb}] {C.rkj}➸❥ {C.pr}{pattern}")
                    print(f"{C.g}    |\n    └── {C.r}Pattern {C.g}➸❥ {C.pr}{pattern}")
                    open(file_path, 'w', encoding='utf-8', errors='ignore').write(new_content)
            except Exception as e:
                pass
    print(f"\n{C.r}{'_' * 61}\n")

# Check_CoreX
def Check_CoreX(decompile_dir, isAPKTool):
    lib_paths = C.os.path.join(decompile_dir, 'lib' if isAPKTool else f'root{C.os.sep}lib')
    Lib_CoreX = []
        
    for arch in C.os.listdir(lib_paths):
        for root, _, files in C.os.walk(C.os.path.join(lib_paths, arch)):
            for target_file in ['lib_Pairip_CoreX.so', 'libFirebaseCppApp.so']:
                if target_file in files:
                    Lib_CoreX.append(f"{C.g}{target_file} ➸❥ {C.rkk}{arch}")
    if Lib_CoreX:
        print(f"\n\n{C.lb}[ {C.y}Info {C.lb}] {C.c}Already Added {C.rkj}➸❥ {f' {C.rkj}& '.join(Lib_CoreX)}{C.c} {C.g}✔")
        return True
    return False

# HooK CoreX
def Hook_Core(apk_path, decompile_dir, isAPKTool, package_name):
    with C.zipfile.ZipFile(apk_path, 'r') as zf:
        base_apk = "base.apk" if "base.apk" in zf.namelist() else f"{package_name}.apk"
    try:
        if C.os.name == 'nt' and C.shutil.which("7z"):
            C.subprocess.run(["7z", "e", apk_path, base_apk, "-y"], text=True, capture_output=True)
            with C.zipfile.ZipFile(apk_path) as zf:
                zf.extract(base_apk)
        else:
            if C.shutil.which("unzip"):
                C.subprocess.run(["unzip", "-o", apk_path, base_apk], text=True, capture_output=True)
                with C.zipfile.ZipFile(apk_path) as zf:
                    zf.extract(base_apk)
        print(f'\n{C.lb}[ {C.c}Dump {C.lb}] {C.g}➸❥ {C.rkj}{base_apk}\n')
        Dump_Apk = "libFirebaseCppApp.so"
        C.os.rename(base_apk, Dump_Apk)
        lib_paths = C.os.path.join(decompile_dir, 'lib' if isAPKTool else f'root{C.os.sep}lib')
        Arch_Paths = []
        for lib in C.os.listdir(lib_paths):
            for root, _, files in C.os.walk(C.os.path.join(lib_paths, lib)):
                if 'libpairipcore.so' in files:
                    Arch_Paths.append(root)

        for Arch in Arch_Paths:
            print(f"\n{C.lb}[ {C.c}Arch {C.lb}] {C.g}➸❥ {C.os.path.basename(Arch)}\n")
            C.shutil.copy(Dump_Apk, Arch); C.shutil.copy(F.Pairip_CoreX, Arch);
        print(f'\n{C.lb}[ {C.c}HooK {C.lb}] {C.g}➸❥ {C.rkj}libFirebaseCppApp.so {C.g}✔\n\n{C.lb}[ {C.c}HooK {C.lb}] {C.g}➸❥ {C.rkj}lib_Pairip_CoreX.so {C.g}✔\n')
        C.os.remove(Dump_Apk)

        return True
    except Exception as e:
        print(f"\n{C.lb}[ {C.rd}Error ! {C.lb}] {C.rd} Hook_Core Error: {e} ✘{C.r}")
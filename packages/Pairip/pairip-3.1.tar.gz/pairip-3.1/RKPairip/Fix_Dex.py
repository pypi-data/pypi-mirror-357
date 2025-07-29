from .C_M import CM; C = CM()
from .Files_Check import FileCheck; F = FileCheck(); F.Set_Path()

C_Line = f"{C.r}{'_' * 61}"

# Scan_Application
def Scan_Application(apk_path, manifest_path, d_manifest_path, isAPKTool):
    App_Name = ''
    if not isAPKTool:
        manifest = open(manifest_path, 'r', encoding='utf-8', errors='ignore').read()
        App_Name = C.re.search(r'<application[^>]*android:name="(.*?)"', manifest)
        if App_Name:
            print(f"\n{C.lb}[ {C.c}Match Application {C.lb}] {C.rkj}➸❥ {C.pr}'{C.g}{App_Name[1]}{C.pr}' {C.g} ✔{C.r}\n")
            return App_Name[1]

    if C.os.name == 'posix':
        result = C.subprocess.run(['aapt', 'dump', 'xmltree', apk_path, 'AndroidManifest.xml'], check=True, capture_output=True, text=True)
        App_Name = C.re.search(r'E: application.*[\s\S]*?A: android:name.*="(.*?)"', result.stdout)
        if App_Name:
            print(f"\n{C.lb}[ {C.c}Match Application {C.lb}] {C.rkj}➸❥ {C.pr}'{C.g}{App_Name[1]}{C.pr}' {C.g} ✔{C.r}\n")
            return App_Name[1]

    if not App_Name:
        # Decode_Manifest
        C.subprocess.run(['java', '-jar', F.Axml2Xml_Path, 'd', manifest_path, d_manifest_path], capture_output=True, text=True, check=True)
        manifest = open(d_manifest_path, 'r', encoding='utf-8', errors='ignore').read()
        App_Name = C.re.search(r'<application[^>]*android:name="(.*?)"', manifest)
        if App_Name:
            print(f"\n{C.lb}[ {C.c}Match Application {C.lb}] {C.rkj}➸❥ {C.pr}'{C.g}{App_Name[1]}{C.pr}' {C.g} ✔{C.r}\n")
            return App_Name[1]
            C.os.remove(manifest_path)
    return App_Name[1]

# Delete Pairip Folder
def Delete_Folders(smali_folders):
    print(f"{C_Line}\n\n\n{C.lb}[ {C.pr}* {C.lb}] {C.c} Deleting Pairip Folders {C.g}✔{C.r}")

    base_dirs = [C.os.path.join("com", "pairip"), "RK_TECHNO_INDIA"]

    for smali_folder in smali_folders:
        for base_dir in base_dirs:
            base_dir_path = C.os.path.join(smali_folder, base_dir)
            if C.os.path.isdir(base_dir_path):
                if base_dir == "RK_TECHNO_INDIA":
                    C.shutil.rmtree(base_dir_path)
                    print(f"{C.g}  |\n  └──── {C.g}Deleting Folder{C.r} ~{C.g}$  {C.y}{C.os.path.basename(base_dir_path)} {C.g}✔{C.r}")
                else:
                    for item in C.os.listdir(base_dir_path):
                        item_path = C.os.path.join(base_dir_path, item)
                        if C.os.path.isdir(item_path):
                            C.shutil.rmtree(item_path)
                            print(f"{C.g}  |\n  └──── {C.g}Deleting Folder{C.r} ~{C.g}$  {C.y}{C.os.path.basename(item_path)} {C.g}✔{C.r}")
                        else:
                            C.os.remove(item_path)
                            print(f"{C.g}  |\n  └──── {C.g}Deleting File{C.r} ~{C.g}$  {C.y}{C.os.path.basename(item_path)} {C.g}✔{C.r}")

    print(f"\n{C_Line}\n\n")

# Search_Target_Strings
def Search_Target_Strings(smali_folders, target_strings):
    matching_files = []; total_matching_files = 0
    
    for smali_folder in smali_folders:
        for root, _, files in C.os.walk(smali_folder):
            for file in files:
                if file.endswith('.smali'):
                    file_path = C.os.path.join(root, file)
                    content = open(file_path, 'r', encoding='utf-8', errors='ignore').read()
                    for target_string in target_strings:
                        if target_string in content:
                            total_matching_files += 1
                            print(f"\r{C.lb}[ {C.pr}* {C.lb}] {C.c} Find Target Smali {C.g}➸❥ {total_matching_files}", end='', flush=True)
                            matching_files.append(file_path)
                            break
    print(f" {C.g}✔", flush=True)
    print(f"\n{C_Line}{C.r}\n")
    return matching_files

# Target String
def Smali_Patcher(smali_folders):
    target_strings = [
        'FuckUByRK',
        'LRK_TECHNO_INDIA/ObjectLogger;->logstring(Ljava/lang/Object;)V',
        'callobjects',
        'const-string/jumbo',
        'pairip'
    ]
    Delete_Folders(smali_folders)
    matching_files = Search_Target_Strings(smali_folders, target_strings)
    if matching_files:
        Apply_Regex(matching_files)
    else:
        pass

# Patches
def Apply_Regex(matching_files):
    patterns = [
        (r'(\.method public static )FuckUByRK\(\)V([\s\S]*?.end method)[\w\W]*', r'\1constructor <clinit>()V\2', "Patch 1"),
        (r'sget-object.*\s+.*const-string v1,(.*\s+).*.line.*\n+.+.*\n.*invoke-static \{v0\}, LRK_TECHNO_INDIA/ObjectLogger;->logstring\(Ljava/lang/Object;\)V', r'const-string v0,\1', "Patch 2"),
        (r'invoke-static \{\}, .*;->callobjects\(\)V\n', r'', "Patch 3"),
        (r'(\.method public.*onReceive\(Landroid/content/Context;Landroid/content/Intent;\)V\s+\.(registers|locals) \d+)[\s\S]*?const-string/jumbo[\s\S]*?(\s+return-void\n.end method)', r'\1\3', "Patch 4"),
        (r'invoke.*pairip/.*', r'', "Patch 5")
    ]

    for pattern, replacement, description in patterns:
        count_applied = 0; applied_files = set()

        for file_path in matching_files:
            content = open(file_path, 'r', encoding='utf-8', errors='ignore').read()

            new_content = C.re.sub(pattern, replacement, content)
            if new_content != content:
                if file_path not in applied_files:
                    applied_files.add(file_path)
                count_applied += 1

                open(file_path, 'w', encoding='utf-8', errors='ignore').write(new_content)

        if count_applied > 0:
            print(f"\n{C.lb}[ {C.c}Patch {C.lb}] {C.g}{description}")
            print(f"\n{C.lb}[ {C.c}Pattern {C.lb}] {C.g}➸❥ {C.pr}{pattern}")
            for file_path in applied_files:
                print(f"{C.g}     |\n     └──── {C.r}~{C.g}$ {C.y}{C.os.path.basename(file_path)} {C.g}✔")
            print(f"\n{C.lb}[ {C.c}Applied {C.lb}] {C.g}➸❥ {C.pr}{count_applied} {C.c}Time/Smali {C.g}✔\n\n{C_Line}\n")

# Translate String
def Replace_Strings(L_S_F, mtd_p):
    mappings = dict(C.re.findall(r'\s"(.*)"\s"(.*)"', open(mtd_p, 'r', encoding='utf-8', errors='ignore').read()))
    #mappings = dict(C.re.findall(r'"([^"]+)"\s(.*)', f.read()))

    file_counter = 0
    for root, _, files in C.os.walk(L_S_F):
        for file in files:
            if file.endswith(".smali"):
                path, line_counter = C.os.path.join(root, file), 1
                lines = open(path, 'r', encoding='utf-8', errors='ignore').readlines()
                with open(path, 'w', encoding='utf-8', errors='ignore') as f:
                    for line in lines:
                        if match := C.re.match(r'\s*const-string v0, "([^"]+)"', line):
                            key = match.group(1)
                            value = mappings.get(key)
                            if value:
                                #line = line.split('"')[0] + f'{value}'
                                line = line.split('"')[0] + f'"{value}"'
                            else:
                                value = f"{file_counter}.java:{line_counter}"
                                #print(f'\n{C.lb}[ {C.y}Warn ! {C.lb}] {C.c} No Value found {C.pr}"{C.g}{key}{C.pr}" {C.g}➸❥ {C.y}{file},{C.c} fallback {C.g}➸❥ {C.pr}"{C.g}{value}{C.pr}"')
                                line = line.split('"')[0] + f'""\n'
                            line_counter += 1
                        f.write(line)
                file_counter += 1
    print(f"\n{C.lb}[ {C.pr}* {C.lb}] {C.c} Translate Dex {C.g}➸❥ {C.pr}{file_counter} {C.c}Time/Smali {C.g}✔\n")
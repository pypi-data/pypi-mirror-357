from .C_M import CM; C = CM()
G = "\n" * 3

def Extract_Smali(decompile_dir, smali_folders, L_S_F, isAPKTool):
    extract_dir = C.os.path.join(decompile_dir, 'smali_classes') if isAPKTool else C.os.path.join(decompile_dir, 'smali', 'classes')
    pattern = C.re.compile(r'\.class public L([^;]+);.*?\n\.super Ljava/lang/Object;\s+# static fields\n\.field public static .*:Ljava/lang/String;')
    folder_suffix = 2; Application_Smali = 0; Pairip_Smali = 0
    moved_files = set(); Smali_Files = set(); Move_App_Smali = False
    while C.os.path.exists(f"{extract_dir}{folder_suffix}"):
        folder_suffix += 1
    extract_dir = f"{extract_dir}{folder_suffix}"
    C.os.makedirs(extract_dir, exist_ok=True)

    print(f"\n{C.lb}[ {C.pr}* {C.lb}] {C.c} Extract Smali {C.r}")
    for root, dirs, files in C.os.walk(L_S_F):
        for file_name in files:
            if file_name.endswith(".smali"):
                Smali_Files.add(C.os.path.join(root, file_name))

    for smali_folder in smali_folders:
        for root, _, files in C.os.walk(smali_folder):
            for file_name in files:
                if file_name.endswith(".smali"):
                    file_path = C.os.path.join(root, file_name)
                    if file_name == "Application.smali" and "com/pairip/application" in file_path.replace(C.os.sep, '/'):
                        if not Move_App_Smali:
                            
                            relative_path = "com/pairip/application/Application.smali"
                            Application_Smali += 1
                            Move_App_Smali = True
                        else: continue
                    else:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                            content = file.read()
                            match = pattern.search(content)
                            if match:
                                relative_path = match[1].replace("/", C.os.sep) + ".smali"
                                if relative_path not in moved_files:
                                    Pairip_Smali += 1
                                    moved_files.add(relative_path)
                                else: continue
                            else: continue

                    target_path = C.os.path.join(extract_dir, relative_path)
                    C.os.makedirs(C.os.path.dirname(target_path), exist_ok=True)
                    C.shutil.move(file_path, target_path)

                    print(f"{C.g}  |\n  └──── {C.r} Moved ~{C.g}$ {C.y}{C.os.path.basename(file_path)} {C.g}➸❥ {C.y}{C.os.path.basename(extract_dir)} {C.g}✔")
    print(f"\n\n{C.lb}[ {C.pr}* {C.lb}] {C.c} Pattern 1 Applied {C.g}➸❥ {C.pr}{Application_Smali} {C.c}Application Smali {C.g}✔")
    print(f"\n{C.lb}[ {C.pr}* {C.lb}] {C.c} Pattern 2 Applied {C.g}➸❥ {C.pr}{Pairip_Smali} {C.c}Pairip Smali {C.g}✔")
    print(f"\n{C.r}{'_' * 61}\n")

# Logs_Injected
def Logs_Injected(L_S_F):
    print(f"\n{C.lb}[ {C.pr}* {C.lb}] {C.c} Last Smali Folder {C.g}➸❥ {C.y}{C.os.path.basename(L_S_F)} {C.g}✔{G}{C.lb}[ {C.cp}* {C.lb}] {C.c} Logs Inject in Target SMALI")
    Class_Names = []; Last_Smali_Path = None
    Sequence = 1; Logs_Inject = 0
        
    for root, _, files in C.os.walk(L_S_F):
        for file in files:
            path = C.os.path.join(root, file)
            content = open(path, 'r', encoding='utf-8', errors='ignore').read()

            Class_Match = C.re.search(r'\.class.* L([^;]+);', content)
            Static_Fields = C.re.findall(r'\.field public static (\w+):Ljava/lang/String;', content)

            if Class_Match and Static_Fields:
                Class_Names.append(Class_Match[1])
                content = C.re.sub(r'(\.super Ljava/lang/Object;)', rf'\1\n.source "{Sequence:1d}.java"', content)

                log_method = ['.method public static FuckUByRK()V', '    .registers 2']
                for i, field in enumerate(Static_Fields):
                    log_method += [
                        f'    sget-object v0, L{Class_Match[1]};->{field}:Ljava/lang/String;',
                        f'    const-string v1, "{Sequence:1d}.java:{i+1}"',
                        f'    .line {i+1}',
                        f'    .local v0, "{Sequence:1d}.java:{i+1}":V',
                        f'    invoke-static {{v0}}, LRK_TECHNO_INDIA/ObjectLogger;->logstring(Ljava/lang/Object;)V',
                        f'    sput-object v0, L{Class_Match[1]};->{field}:Ljava/lang/String;'
                    ]
                log_method += ['    return-void', '.end method']
                content += '\n' + '\n'.join(log_method)

                open(path, 'w', encoding='utf-8', errors='ignore').write(content)

                print(f"{C.g}  |\n  └──── {C.r}Logs Inject ~{C.g}$ ➸❥ {C.y}{C.os.path.basename(path)}{C.g} ✔")
                Last_Smali_Path = path; Sequence += 1; Logs_Inject += 1

    print(f"\n{C.lb}[ {C.pr}* {C.lb}] {C.c} Total Smali {C.pr}{Logs_Inject} {C.g}✔\n")

    if Class_Names and Last_Smali_Path:
        print(f'\n{C.lb}[ {C.cp}* {C.lb}] {C.c} Callobjects Call Inject in Target SMALI {C.g}✔\n')

        code = ('\n.method public static callobjects()V\n\t'
                '.registers 2\n\t' +
                ''.join(f'invoke-static {{}}, L{CN};->FuckUByRK()V\n\t' for CN in Class_Names) +
                'return-void\n.end method\n')

        open(Last_Smali_Path, 'a', encoding='utf-8', errors='ignore').write(code)

        print(f"{C.g}  |\n  └──── {C.r}Added Callobjects ~{C.g}$ ➸❥ {C.y}{C.os.path.basename(Last_Smali_Path)}{C.g} ✔\n")

    Application_Class = C.os.path.join(L_S_F, 'com', 'pairip', 'application', 'Application.smali')

    if Last_Smali_Path and C.os.path.exists(Application_Class):
        print(f'\n{C.lb}[ {C.cp}* {C.lb}] {C.c} Callobjects Call Hook in Target SMALI {C.g}✔\n')
        C_Name = C.os.path.splitext(C.os.path.relpath(Last_Smali_Path, L_S_F).replace(C.os.sep, "/"))[0]

        content = open(Application_Class, 'r', encoding='utf-8', errors='ignore').read()

        Hook_Callobjects = C.re.sub(r'(\.method public constructor <init>\(\)V[\s\S]*?)(\s+return-void\n.end method)', rf'\1\n\tinvoke-static {{}}, L{C_Name};->callobjects()V\n\2', content)

        open(Application_Class, 'w', encoding='utf-8', errors='ignore').write(Hook_Callobjects)

        print(f"{C.g}  |\n  └──── {C.r}Hook Callobjects ~{C.g}$ ➸❥ {C.y}{C.os.path.basename(Application_Class)}{C.g} ✔\n")

    print(f"\n{C.lb}[ {C.pr}* {C.lb}] {C.c} Patching Done {C.g}✔\n")
    print(f"{C.r}{'_' * 61}\n")
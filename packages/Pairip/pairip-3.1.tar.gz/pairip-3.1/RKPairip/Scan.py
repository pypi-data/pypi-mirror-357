from .C_M import CM;  C = CM()
from .Files_Check import FileCheck; F = FileCheck(); F.Set_Path()

G2 = "\n" * 2

def Scan_Apk(apk_path):
    print(f"\n{C.r}{'_' * 61}\n")
    Application_Name = False; Pairip = False; Package_Name = ''
    
    # Extract Package Name
    if C.os.name == 'posix':
        result = C.subprocess.run(['aapt', 'dump', 'badging', apk_path], capture_output=True, text=True)
        pkg_name = C.re.search(r"package: name='([^']+)'", result.stdout)
        if pkg_name:
            Package_Name = pkg_name[1]
            print(f"\n{C.lb}[ {C.c}Package Name {C.lb}] {C.rkj}➸❥ {C.pr}'{C.g}{Package_Name}{C.pr}' {C.g} ✔{C.r}\n")

        # Match Application Name
        result = C.subprocess.run(['aapt', 'dump', 'xmltree', apk_path, 'AndroidManifest.xml'], capture_output=True, text=True)
        app_name = C.re.search(r'A: android:name\(.*\)="com\.pairip\.application\.Application"', result.stdout)
        if app_name:
            print(f"\n{C.lb}[ {C.c}Application Name {C.lb}] {C.rkj}➸❥ {C.pr}'{C.g}com.pairip.application.Application{C.pr}' {C.g} ✔{C.r}\n")
            Application_Name = True

    #  Extract Package Name with APKEditor
    if not Package_Name:
        cmd = ["java", "-jar", F.APKEditor_Path, "info", "-package", "-i", apk_path]
        result = C.subprocess.run(cmd, capture_output=True, text=True)
        Package_Name = result.stdout.split('"')[1]
        print(f"\n{C.lb}[ {C.c}Package Name {C.lb}] {C.rkj}➸❥ {C.pr}'{C.g}{Package_Name}{C.pr}'{C.g}  ✔{C.r}\n")

    # Check for APK protections
    Detect_Protection = []
    with C.zipfile.ZipFile(apk_path, 'r') as zip_ref:
        for item in zip_ref.infolist():
            if item.filename.startswith('lib/'):
                if item.filename.endswith('libpairipcore.so'):
                    print(f"\n{C.lb}[ {C.c}Pairip Protection {C.lb}] {C.rkj}➸❥ {C.pr}'{C.g}Google加固{C.pr}' {C.g} ✔")
                    Pairip = True
        
    if not Application_Name and not Pairip: exit(f"{C.rd} Your APK Has No Pairip Protection ✘{C.r}\n")

    def Check_Lib():
        unity_libs = []; flutter_libs = []; dex_files = []

        with C.zipfile.ZipFile(apk_path, 'r') as zip_ref:
            for item in zip_ref.infolist():
                if item.filename.startswith('lib/'):
                    if item.filename.endswith(('libunity.so', 'libil2cpp.so')):
                        unity_libs.append(item.filename)
                    if item.filename.endswith('libflutter.so'):
                        flutter_libs.append(item.filename)
                elif item.filename.startswith("classes") and item.filename.endswith('.dex'):
                    dex_files.append(item.filename)

            methods = fields = 0

            if dex_files:
                try:
                    data = zip_ref.open(dex_files[-1], 'r').read()
                    methods = int.from_bytes(data[88:91], "little")
                    fields = int.from_bytes(data[80:83], "little")
                except (OSError, ValueError, KeyError, C.zipfile.BadZipFile) as e:
                    print(f"{G2}{C.lb}[ {C.y}WARN ! {C.lb}] {C.rd}{e}, Skipping Methods & Fields Count.")

        if unity_libs:
            print(f"{G2}{C.lb}[ {C.c}Unity Protection {C.lb}] {C.rkj}➸❥ {C.pr}'{C.g}{', '.join(C.os.path.basename(lib) for lib in unity_libs)}{C.c}' {C.g} ✔{G2}{C.lb}[ {C.y}WARN ! {C.lb}] {C.rd}This is a Unity app. Completely removing Pairip may not be possible unless you can bypass the libpairipcore.so check from Unity libraries.")
        if flutter_libs:
            print(f"{G2}{C.lb}[ {C.c}Flutter Protection {C.lb}] {C.rkj}➸❥ {C.pr}'{C.g}{', '.join(C.os.path.basename(lib) for lib in flutter_libs)}{C.pr}'{C.g} ✔\n\n\n{C.lb}[ {C.y}WARN ! {C.lb}] {C.rd}This is a Flutter app. It may not run directly after removing pairip, unless you can bypass the libpairipcore.so check from Flutter libraries.")
        if methods and fields:
            print(f"{G2}{C.lb}[{C.y} Last Dex Total {C.lb}] {C.c}Methods: {C.rkj}{methods} {C.g}➸❥ {C.c}Field: {C.rkj}{fields}  {C.g}✔")
        else:
            pass

    Check_Lib()
    return Package_Name
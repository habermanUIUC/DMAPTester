def install_info490_repo(reload=False):
    try:
        import os, sys
        INSTALL_PATH = '/content/info490'  # keep as is
        if not os.path.exists(INSTALL_PATH):
            os.mkdir(INSTALL_PATH)
        !git
        clone
        https: // github.com / NSF - EC / INFO490Assets.git
        info490 / INFO490Assets
        !git
        clone
        https: // github.com / habermanUIUC / DMAPTester.git
        info490 / DMAPTester
        if reload:
            !cd
            info490 / INFO490Assets;
            git
            pull;
            cd..
            !cd
            info490 / DMAPTester;
            git
            pull;
            cd..

        ASSET_PATH = "{:s}/{:s}".format(INSTALL_PATH, "INFO490Assets/src")
        if ASSET_PATH not in sys.path:
            sys.path.append(ASSET_PATH)
        from tools import IDE
        if reload:
            import importlib
            importlib.reload(IDE)
        return IDE.ColabIDE(LESSON_ID, NOTEBOOK_ID, reload=reload)
    except Exception as e:
        class Nop(object):
            def __init__(self, e): self.e = e

            def nop(self, *args, **kw): return ("unable to test:" + self.e, None)

            def __getattr__(self, _): return self.nop

        class IDE():
            tester = Nop(str(e))
            reader = Nop(str(e))

        return IDE()1
from PyInstaller.utils.hooks import copy_metadata, collect_submodules

datas = copy_metadata('typeguard')
hiddenimports = collect_submodules('typeguard')

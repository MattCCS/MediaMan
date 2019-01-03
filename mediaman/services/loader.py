

def load(name):
    if name == "local":
        return load_local()
    elif name == "drive":
        return load_drive()
    else:
        raise NotImplementedError()


def load_all():
    return [
        load_local(),
        load_drive(),
    ]


def load_drive():
    from mediaman.services.drive import service as driveservice
    return driveservice.DriveService()


def load_local():
    from mediaman.services.local import service as localservice
    return localservice.LocalService()

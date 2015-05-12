from autohdl import manager
# There are 3 scopes while setting design configuration.
# Priority: 1 - argument list, 2 - this script, 3 - build.yaml

manager.kungfu(
    # Set top module name.
    # top = '',

    # Set constraint file.
    # Could be a valid relative path (keep in mind repo)
    # or just a name, if it locates in the current design folder.
    # ucf = '',

    # Set flash size (e.g. 256, 512)
    # size = '',

    # Uncomment to upload firmware on WebDAV server.
    # upload = True
)

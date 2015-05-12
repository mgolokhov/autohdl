from autohdl import manager
# There are 3 scopes while setting design configuration.
# Priority: 1 - argument list, 2 - this script, 3 - build.yaml

manager.kungfu(
    # Set top module name.
    # iTop = '',

    # Set constraint file.
    # Could be a valid relative path (keep in mind repo)
    # or just a name, if it locates in the current design folder.
    # iUcf = '',

    # Set flash size (*examples*)
    # iSize = '',

    # Uncomment to upload firmware on WebDAV server.
    # iUpload = 'True'
)


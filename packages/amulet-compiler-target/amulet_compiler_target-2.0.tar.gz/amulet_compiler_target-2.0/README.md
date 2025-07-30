# Amulet-Compiler-Target

This library exists to ensure that all of our libraries are compiled using the same settings
because PyPi and Pip lack tooling to ensure that the Application Binary Interface (ABI)
of multiple separately compiled libraries remain compatible.

The requirements for each version are defined in the versionX.md files.

Each of our libraries must include this as a pinned runtime dependency to ensure that only
libraries compatible with these settings can be installed.

# Semantic Versioning

Our libraries use semantic versioning in the format MAJOR.MINOR.PATCH.SUB however this is for API not ABI.

A MAJOR change breaks API and ABI compatibility.

A MINOR change is a backwards compatible API change but should be considered a breaking ABI change.

A PATCH change must not change the API or ABI.

A SUB change can be used if the code has not changed but we want to update the compiler target version.

The source distribution requirements must be in the form `library ~= 1.1`

Compiled distribution requirements must be in the form `library ~= 1.1.0`

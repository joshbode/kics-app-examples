# Shared file reader and writer

This is a simple example that shows two different workloads sharing the same host path/file.

`shared-file-writer` Writes a random integer value in each second to the shared file.

`shared-file-reader` project reads the shared file for each second and prints the last line.

**Note: The shared file lives in the host environment.**

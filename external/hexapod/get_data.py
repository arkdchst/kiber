
def write_data(pid, mode):
    out_file = open("file.txt", "w")

    out_file.write(pid)

    out_file.write("\r\n")

    out_file.write(mode)

    out_file.close()


def read_data():
    in_file = open("file.txt", "r")

    pid = in_file.readline()

    pid = pid[:(len(pid)-1)]

    mode = in_file.readline()

    in_file.close()

    return [pid, mode]




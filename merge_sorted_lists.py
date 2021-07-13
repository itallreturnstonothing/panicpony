import argparse
import os

def validate(ids_file):
    ids_file.seek(0)
    def wew():
        curr = read_id(ids_file)
        new = read_id(ids_file)
        while new:
            yield (curr, new)
            curr = new
            new = read_id(ids_file)
    assert all((a < b) for (a, b) in wew())




def read_id(ids_file):
    attempt = ids_file.read(20)
    if len(attempt) == 20:
        return attempt[8:19]
    else:
        return None

def write_id(vid_id, output):
    output.write(f"youtube {vid_id}\n")

def merge(f1, f2, output):
    def end(curr_id, file_still_has_lines):
        write_id(curr_id, output)
        output.write(file_still_has_lines.read())
    f1_id = read_id(f1)
    f2_id = read_id(f2)
    while f1_id and f2_id:
        if f1_id == f2_id:
            write_id(f1_id, output)
            f1_id = read_id(f1)
            f2_id = read_id(f2)
        elif f1_id < f1_id:
            write_id(f1_id, output)
            f1_id = read_id(f1)
        elif f2_id < f1_id:
            write_id(f2_id, output)
            f2_id = read_id(f2)
        else:
            # should never reach here
            raise Exception("something is wrong")
    if f2_id:
        # reached end of file 1
        end(f2_id, f2)
    if f1_id:
        # reached end of file 2
        end(f1_id, f1)




if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "f1",
        help="first file to merge"
    )

    parser.add_argument(
        "f2",
        help="second file to merge"
    )

    parser.add_argument(
        "output",
        help="output file"
    )

    args = parser.parse_args()
    f1 = None
    f2 = None
    output = None
    try:
        f1_name = os.path.expanduser(args.f1)
        f2_name = os.path.expanduser(args.f2)
        out_name = os.path.expanduser(args.output)
        f1 = open(f1_name)
        f2 = open(f2_name)
        output = open(out_name, "w")
    except Exception as e:
        print("failed while opening a file")
        print(e)
        if f1:
            f1.close()
        if f2:
            f2.close()
        if output:
            output.close()
        exit()


    with f2, f2, output:
        validate(f1)
        print("file 1 good")
        validate(f2)
        print("file 2 good")
        f1.seek(0)
        f2.seek(0)
        merge(f1, f2, output)
        

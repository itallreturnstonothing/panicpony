
line_length = 20    # length of each line including the newline
                    # example: "youtube --GdlhQqIrc\n" is length 20
total_lines = 101 #415741

# read the video id from ids_file at the current position.
# the current position better be at the start of a line.
def read_id(ids_file, return_to_staring_position=True):
    starting_position = ids_file.tell()
    vid_id = ids_file.read(20)[8:19]
    if return_to_staring_position:
        ids_file.seek(starting_position)
    return vid_id.decode()



def binary_search_for_id(vid_id, ids_file, actual_total_lines=None):
    threshold = 100
    def do_search(lower_bound, upper_bound):
        #print(f"{lower_bound} {upper_bound}")
        if ( upper_bound - lower_bound ) <= threshold:
            # construct a list of ids and search it.
            # the list will be at most threshold items large, so it should be 
            # small enough to search quickly. 

            # seek to beginning of search region
            ids_file.seek(lower_bound * line_length)

            # make list (actually a generator, same effect)
            search_these = (read_id(ids_file, False) for _ in range(upper_bound - lower_bound))

            return vid_id in search_these

        else: # do binary search

            # get the id at the midpoint
            divide_in_half = (upper_bound - lower_bound) >> 1 # integer division by 2
            midpoint = lower_bound + divide_in_half
            # seek file to midpoint
            ids_file.seek(midpoint * line_length)
            id_at_midpoint = read_id(ids_file)

            # narrow the search region
            if vid_id >= id_at_midpoint:
                # search midpoint to upper_bound
                lower_bound = midpoint
            else:
                # search lower_bound to midpoint
                upper_bound = midpoint

            return do_search(lower_bound, upper_bound)

    return do_search(0, actual_total_lines if actual_total_lines else total_lines)


def filter_for_unknown(vid_ids, ids_filename, actual_total_lines):
    with open(ids_filename, "rb") as ids_file:
        return list(
            filter(
                lambda x: not binary_search_for_id(x, ids_file, actual_total_lines),
                vid_ids
            )
        )




if __name__ == "__main__":
    import timeit
    import random
    with open("already_archived_list.txt", "rb") as ids_file:
        all_ids = []
        print("constructing all_ids")
        for _ in range(total_lines):
            all_ids.append(read_id(ids_file, False))

        print("done")
        print(all(binary_search_for_id(vid_id, ids_file) for vid_id in all_ids))
        do_not_exist = ['Sz7Ei6KT0jo', 'qJ9wwxHzoXW', '_edaJZx9YCv', '2empZO1zEsB', '_FKgJSJuLl9', 'Swfj3JPEddp', '9v4M2nUz2zl', 'XsTbZ0ta8SN', 'L2mj2G3y0mp', 'sP0ECIxnEOv']
        print(any(binary_search_for_id(vid_id, ids_file) for vid_id in do_not_exist))
        # print("timing search_list")
        # def search_list(all_ids):
        #     sample = random.sample(all_ids, 100)
        #     for vid_id in sample:
        #         t = vid_id in all_ids
        # print(timeit.repeat("search_list(all_ids)", setup = "from __main__ import search_list, all_ids", repeat=5, number=10))
        # print("timing b_search")
        def b_search(all_ids, thr):
            sample = random.sample(all_ids, 100)
            for vid_id in sample:
                t = binary_search_for_id(vid_id, ids_file, thr)

        # 100 is just fine
        # print(timeit.repeat("b_search(all_ids)", setup = "from __main__ import b_search, all_ids", repeat=5, number=10))
        # print("50 - ", end="")
        # print(round(min(timeit.repeat("b_search(all_ids, 50)", setup = "from __main__ import b_search, all_ids", repeat=5, number=10)), 5))
        # print("100 - ", end="")
        # print(round(min(timeit.repeat("b_search(all_ids, 100)", setup = "from __main__ import b_search, all_ids", repeat=5, number=10)), 5))
        # print("200 - ", end="")
        # print(round(min(timeit.repeat("b_search(all_ids, 200)", setup = "from __main__ import b_search, all_ids", repeat=5, number=10)), 5))
        # print("500 - ", end="")
        # print(round(min(timeit.repeat("b_search(all_ids, 500)", setup = "from __main__ import b_search, all_ids", repeat=5, number=10)), 5))
        # print("1000 - ", end="")
        # print(round(min(timeit.repeat("b_search(all_ids, 1000)", setup = "from __main__ import b_search, all_ids", repeat=5, number=10)), 5))




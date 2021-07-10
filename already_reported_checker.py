import io

line_length = 20    # length of each line including the newline
                    # example: "youtube --GdlhQqIrc\n" is length 20
total_lines = 101 #415741

# read the video id from ids_file at the current position.
# the current position better be at the start of a line.
def read_id(ids_file, return_to_staring_position=True):
    starting_position = ids_file.tell()
    ids_file.seek(8, io.SEEK_CUR)
    vid_id = ids_file.read(12)[:-1]
    if return_to_staring_position:
        ids_file.seek(starting_position)
    return vid_id.decode()



def binary_search_for_id(vid_id, ids_file):
    def do_search(vid_id, ids_file, lower_bound, upper_bound, threshold):
        #print(f"{lower_bound} {upper_bound}")
        if ( upper_bound - lower_bound ) <= threshold:
            # just start looping through lines
            position_of_last_line = upper_bound * line_length
            # seek to start
            ids_file.seek(lower_bound * line_length)
            while ids_file.tell() < position_of_last_line:
                check_id = read_id(ids_file, False)
                #print(check_id)
                if check_id == vid_id:
                    # there it is
                    return True
            # checked all ids between upper and lower bound,
            # didn't find the id we were looking for. 
            return False
        else: # do binary search
            half_lines = (upper_bound - lower_bound) >> 1 # integer division by 2
            midpoint = lower_bound + half_lines
            # seek file to midpoint
            ids_file.seek(midpoint * line_length)
            id_at_midpoint = read_id(ids_file)
            if vid_id >= id_at_midpoint:
                # search midpoint to upper_bound
                lower_bound = midpoint
            else:
                # search lower_bound to midpoint
                upper_bound = midpoint
            return do_search(vid_id, ids_file, lower_bound, upper_bound, threshold)

    # with open("already_archived_list.txt", "rb") as ids_file:
    #     return do_search(vid_id, ids_file, 0, total_lines, 10)
    return do_search(vid_id, ids_file, 0, total_lines, 100)


if __name__ == "__main__":
    import timeit
    import random
    with open("already_archived_list.txt", "rb") as ids_file:
        all_ids = []
        print("constructing all_ids")
        for _ in range(total_lines):
            all_ids.append(read_id(ids_file, False))

        print("done")
        # print(all(binary_search_for_id(vid_id, ids_file) for vid_id in all_ids))
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




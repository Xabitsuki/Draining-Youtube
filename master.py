from master_functions import *
url_lst = ['https://www.youtube.com/watch?v=9Ax-JrJ06fU']
id_lst = []
sample=True

if __name__ == '__main__':
    ## Capture
    # Todo: download and prepare folder for the list
    for url in url_lst:
        v_id = capture(url, sample=sample)
        id_lst.append(v_id)

    ## Drain
    # Todo: run first iter_0 for each video + split in sets
    for id in id_lst:
        iter0(id)
        pth_sets = make_sets(id)
        remove_ds_store(pth_sets)
        for set in path_sets:
            sfm_pipe
    # Todo: incremental looping and cleaning


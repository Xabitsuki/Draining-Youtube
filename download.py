from functions import yt_dl

print('Start download of playlist : {}\n'.format(PLAYLIST))
yt_dl(url= URL,
      playlist=PLAYLIST,
      n_items= N_ITEMS)
print('Finish download of playlist : {}\n'.format(PLAYLIST))

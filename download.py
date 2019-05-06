URL = 'https://www.youtube.com/watch?v=FVj8yg9ZVMA&list=PLHEt6c_hdjLtU0Qr41tOVzDJPTwbAx0zu''
PLAYLIST = 'SHIBUYA STREET VIEW - WALKING TOUR'
N_ITEMS = 10

print('Start download of playlist : {}\n'.format(PLAYLIST))
yt_dl(url= URL,
      playlist=PLAYLIST,
      n_items= N_ITEMS)
print('Finish download of playlist : {}\n'.format(PLAYLIST))

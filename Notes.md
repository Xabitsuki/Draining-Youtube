# Notes
##### Where to run the scripts ? 
The scripts are supposed to be ran from the main project folder
that contains the script being ran and the `videos/` folder. 

##
- ``id``: identifier of a youtube video. 
To find the video online one needs to got to page: 
``https://youtube.com/watch?v=id``
_Example_ : ``id = RgKAFK5djSk` leads to the top 3 most viewed 
video of youtube at the adress https://youtube.com/watch?v=RgKAFK5djSk

## Docs: 

#### yt_dl(url, playlist=' ', n_items=1, opts={})
- if ´plylst´ directory does not exist, it is created automatically. 


### Results

extracting frames from a 30 sec 4k video takes ~ 

#### 1920x1080 6 minutes video : 

- storage required : ~3Go
- execution time : 


### Details 

#### OpenMVG 

- focal : as the details of the sensors and objectives

### Terminal actions :

#### Youtube dl 

`youtube-dl {url}`

#### Avconv

`avconv -i {file} -ss {start time in s} -t {stop time in s} -codec copy {new file path}`

### TODO

- faire des moves dans le ficheir frame au moment de la 3D

### Possible improvements : 

- parallelize some actions : 
    - such as rien the moving of the frames
    
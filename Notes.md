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

#### What does not work ?

Frames where not enough movement is perceived do lead to 
a failure of openmvg who does not succeed to construct a 
3D model out of it.  

#### Shibuya playlist 

- Most of the frames do not find are not put in a set and hence,
 are not used in the incremental. 
 

#### 1920x1080 6 minutes video : 

- storage required : ~3Go
- execution time :
    - computeMVG_main_ComputeMatches : ~1h30


### Details 

#### OpenMVG 

- focal : as the details of the sensors and objectives

### Terminal actions :

#### Youtube dl 

`youtube-dl {url}`

#### Avconv

`avconv -i {file} -ss {start time in s} -t {stop time in s} -codec copy {new file path}`

### TODO

implement the remove of unnecessary files 
write start_project.py file asking for the name of folder to begin draining 